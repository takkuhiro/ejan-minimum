"""Tutorial structure service using Gemini Structured Output."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, field_validator

from app.services.ai_client import AIClient, AIClientAPIError


class TutorialStructureError(Exception):
    """Exception raised during tutorial structure generation."""

    pass


class Tool(BaseModel):
    """Represents a makeup tool or product."""

    name: str = Field(..., min_length=1, description="Name of the tool")
    description: str = Field(..., description="Description of the tool's purpose")


class MakeupStep(BaseModel):
    """Represents a single step in the makeup tutorial."""

    step_number: int = Field(..., ge=1, description="Step number in sequence")
    title: str = Field(..., min_length=1, description="Title of the step")
    description: str = Field(..., description="Detailed description of the step")
    duration_seconds: int = Field(default=30, ge=10, description="Duration in seconds")
    tools_needed: List[str] = Field(
        default_factory=list, description="List of tools needed"
    )


class MakeupProcedure(BaseModel):
    """Complete makeup procedure with all steps and tools."""

    title: str = Field(..., min_length=1, description="Title of the makeup look")
    description: str = Field(..., description="Description of the overall look")
    total_duration_minutes: int = Field(
        ..., ge=1, description="Total duration in minutes"
    )
    difficulty_level: str = Field(..., description="Difficulty level")
    steps: List[MakeupStep] = Field(..., min_length=1, description="List of steps")
    required_tools: List[Tool] = Field(..., description="List of required tools")

    @field_validator("difficulty_level")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        """Validate difficulty level."""
        valid_levels = ["beginner", "intermediate", "advanced"]
        if v.lower() not in valid_levels:
            raise ValueError(f"Difficulty must be one of {valid_levels}")
        return v.lower()


def generate_tutorial_prompt(
    style_description: str,
    gender: Optional[str] = None,
    custom_request: Optional[str] = None,
) -> str:
    """Generate prompt for tutorial structure creation.

    Args:
        style_description: Description of the style to create tutorial for.
        gender: Optional gender specification.
        custom_request: Optional custom request text.

    Returns:
        Generated prompt string.
    """
    base_prompt = f"""Create a detailed step-by-step makeup and hairstyling tutorial for achieving the following style:
{style_description}

Provide a complete tutorial with:
1. Clear title and description
2. Step-by-step instructions with specific techniques
3. Time estimate for each step
4. Required tools and products
5. Overall difficulty level (beginner, intermediate, or advanced)

Make the Japanese instructions clear and easy to follow for someone learning this style."""

    if gender:
        gender_text = {
            "male": "for men",
            "female": "for women",
            "neutral": "as gender-neutral",
        }.get(gender.lower(), "")
        if gender_text:
            base_prompt += f"\n\nTailor the tutorial {gender_text}."

    if custom_request:
        base_prompt += f"\n\nAdditional requirements: {custom_request}"

    return base_prompt


class TutorialStructureService:
    """Service for generating structured tutorials using Gemini."""

    def __init__(self, ai_client: AIClient):
        """Initialize tutorial structure service.

        Args:
            ai_client: AI client for Gemini API.
        """
        self.ai_client = ai_client
        self.model_name = (
            "gemini-2.0-flash-exp"  # または gemini-1.5-flash など利用可能なモデル
        )

    async def generate_tutorial_structure(
        self,
        style_description: str,
        gender: Optional[str] = None,
        custom_request: Optional[str] = None,
    ) -> MakeupProcedure:
        """Generate structured tutorial for a style.

        Args:
            style_description: Description of the style.
            gender: Optional gender specification.
            custom_request: Optional custom request.

        Returns:
            Structured makeup procedure.

        Raises:
            TutorialStructureError: If generation fails.
        """
        try:
            # Generate prompt
            prompt = generate_tutorial_prompt(style_description, gender, custom_request)

            # Call AI API with structured output using Pydantic model
            response_data = self.ai_client.generate_structured_output(
                model=self.model_name,
                prompt=prompt,
                response_schema=MakeupProcedure,  # Pass the Pydantic model class directly
            )

            # If response is already a MakeupProcedure object, use it
            if isinstance(response_data, MakeupProcedure):
                procedure = response_data
            else:
                # Otherwise parse from dict
                try:
                    procedure = MakeupProcedure(**response_data)
                except Exception as e:
                    raise TutorialStructureError(f"Invalid tutorial structure: {e}")

            # Additional validation
            if not self.validate_procedure(procedure):
                raise TutorialStructureError("Generated procedure failed validation")

            return procedure

        except AIClientAPIError as e:
            raise TutorialStructureError(f"Failed to generate tutorial structure: {e}")
        except Exception as e:
            raise TutorialStructureError(f"Unexpected error: {e}")

    def get_response_schema(self) -> Dict[str, Any]:
        """Get JSON schema for structured response.

        Returns:
            JSON schema dictionary.
        """
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "total_duration_minutes": {"type": "integer"},
                "difficulty_level": {"type": "string"},
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "step_number": {"type": "integer"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "duration_seconds": {"type": "integer"},
                            "tools_needed": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["step_number", "title", "description"],
                    },
                },
                "required_tools": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                        },
                        "required": ["name", "description"],
                    },
                },
            },
            "required": [
                "title",
                "description",
                "total_duration_minutes",
                "difficulty_level",
                "steps",
                "required_tools",
            ],
        }

    def validate_procedure(self, procedure: MakeupProcedure) -> bool:
        """Validate generated procedure.

        Args:
            procedure: Procedure to validate.

        Returns:
            True if valid, False otherwise.
        """
        # Check minimum requirements
        if len(procedure.steps) == 0:
            return False

        # Check step numbers are sequential
        step_numbers = [step.step_number for step in procedure.steps]
        expected_numbers = list(range(1, len(procedure.steps) + 1))
        if sorted(step_numbers) != expected_numbers:
            return False

        # Check duration is reasonable
        if procedure.total_duration_minutes > 120:  # Max 2 hours
            return False

        return True

    def calculate_total_duration(self, steps: List[MakeupStep]) -> int:
        """Calculate total duration from steps.

        Args:
            steps: List of makeup steps.

        Returns:
            Total duration in minutes.
        """
        total_seconds = sum(step.duration_seconds for step in steps)
        return (total_seconds + 59) // 60  # Round up to nearest minute

    async def enrich_with_details(self, procedure: MakeupProcedure) -> MakeupProcedure:
        """Enrich procedure with additional details if needed.

        Args:
            procedure: Base procedure to enrich.

        Returns:
            Enriched procedure.
        """
        # This is a placeholder for future enhancements
        # Could add image generation for each step, video prompts, etc.
        return procedure

    def format_for_response(self, procedure: MakeupProcedure) -> Dict[str, Any]:
        """Format procedure for API response.

        Args:
            procedure: Procedure to format.

        Returns:
            Formatted dictionary for API response.
        """
        return {
            "title": procedure.title,
            "description": procedure.description,
            "total_duration_minutes": procedure.total_duration_minutes,
            "difficulty_level": procedure.difficulty_level,
            "steps": [
                {
                    "step_number": step.step_number,
                    "title": step.title,
                    "description": step.description,
                    "duration_seconds": step.duration_seconds,
                    "tools_needed": step.tools_needed,
                }
                for step in procedure.steps
            ],
            "tools": [
                {"name": tool.name, "description": tool.description}
                for tool in procedure.required_tools
            ],
        }

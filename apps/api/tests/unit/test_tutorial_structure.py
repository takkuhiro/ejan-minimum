"""Unit tests for tutorial structure service."""

from typing import Dict, Any
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from app.services.tutorial_structure import (
    TutorialStructureService,
    TutorialStructureError,
    MakeupStep,
    MakeupProcedure,
    Tool,
    generate_tutorial_prompt,
)
from app.services.ai_client import AIClient


class TestDataModels:
    """Test tutorial data models."""

    def test_tool_model_valid(self) -> None:
        """Test valid Tool model creation."""
        tool = Tool(
            name="Foundation Brush",
            description="A flat brush for applying foundation evenly",
        )
        assert tool.name == "Foundation Brush"
        assert tool.description == "A flat brush for applying foundation evenly"

    def test_tool_model_validation(self) -> None:
        """Test Tool model validation."""
        with pytest.raises(ValidationError):
            Tool(name="", description="Description")  # Empty name

        with pytest.raises(ValidationError):
            Tool(name="Brush")  # Missing description

    def test_makeup_step_model_valid(self) -> None:
        """Test valid MakeupStep model creation."""
        step = MakeupStep(
            step_number=1,
            title="Apply Foundation",
            description="Apply foundation evenly across the face",
            duration_seconds=60,
            tools_needed=["Foundation", "Foundation Brush"],
        )
        assert step.step_number == 1
        assert step.title == "Apply Foundation"
        assert step.duration_seconds == 60
        assert len(step.tools_needed) == 2

    def test_makeup_step_model_defaults(self) -> None:
        """Test MakeupStep model with defaults."""
        step = MakeupStep(
            step_number=1, title="Test Step", description="Test description"
        )
        assert step.duration_seconds == 30  # Default duration
        assert step.tools_needed == []  # Default empty list

    def test_makeup_procedure_model_valid(self) -> None:
        """Test valid MakeupProcedure model creation."""
        tool = Tool(name="Brush", description="Makeup brush")
        step = MakeupStep(
            step_number=1,
            title="Step 1",
            description="First step",
            tools_needed=["Brush"],
        )

        procedure = MakeupProcedure(
            title="Natural Makeup Look",
            description="A fresh and natural makeup style",
            total_duration_minutes=15,
            steps=[step],
            required_tools=[tool],
        )

        assert procedure.title == "Natural Makeup Look"
        assert procedure.total_duration_minutes == 15
        assert len(procedure.steps) == 1
        assert len(procedure.required_tools) == 1

    def test_makeup_procedure_difficulty_validation(self) -> None:
        """Test MakeupProcedure difficulty level validation."""
        with pytest.raises(ValidationError):
            MakeupProcedure(
                title="Test",
                description="Test",
                total_duration_minutes=10,
                steps=[],
                required_tools=[],
            )


class TestTutorialPromptGeneration:
    """Test tutorial prompt generation."""

    def test_generate_tutorial_prompt_basic(self) -> None:
        """Test basic tutorial prompt generation."""
        prompt = generate_tutorial_prompt(
            style_description="Natural daytime makeup look"
        )

        assert "Natural daytime makeup look" in prompt
        assert "step-by-step" in prompt.lower()
        assert "tutorial" in prompt.lower()
        assert "makeup" in prompt.lower()

    def test_generate_tutorial_prompt_with_gender(self) -> None:
        """Test tutorial prompt with gender specification."""
        prompt = generate_tutorial_prompt(
            style_description="Bold evening look", gender="male"
        )

        assert "Bold evening look" in prompt
        assert "male" in prompt.lower() or "men" in prompt.lower()

    def test_generate_tutorial_prompt_with_custom_request(self) -> None:
        """Test tutorial prompt with custom request."""
        custom = "Focus on eye makeup techniques"
        prompt = generate_tutorial_prompt(
            style_description="Smoky eye look", custom_request=custom
        )

        assert "Smoky eye look" in prompt
        assert custom in prompt


class TestTutorialStructureService:
    """Test tutorial structure service."""

    @pytest.fixture
    def mock_ai_client(self) -> Mock:
        """Create mock AI client."""
        return Mock(spec=AIClient)

    @pytest.fixture
    def service(self, mock_ai_client: Mock) -> TutorialStructureService:
        """Create tutorial structure service instance."""
        return TutorialStructureService(ai_client=mock_ai_client)

    @pytest.fixture
    def sample_procedure_dict(self) -> Dict[str, Any]:
        """Create sample procedure dictionary."""
        return {
            "title": "Natural Daytime Look",
            "description": "A fresh and clean makeup style perfect for everyday wear",
            "total_duration_minutes": 15,
            "steps": [
                {
                    "step_number": 1,
                    "title": "Prep Your Skin",
                    "description": "Cleanse and moisturize your face",
                    "duration_seconds": 60,
                    "tools_needed": ["Cleanser", "Moisturizer"],
                },
                {
                    "step_number": 2,
                    "title": "Apply Foundation",
                    "description": "Apply foundation evenly across your face",
                    "duration_seconds": 90,
                    "tools_needed": ["Foundation", "Foundation Brush"],
                },
            ],
            "required_tools": [
                {
                    "name": "Foundation",
                    "description": "Liquid foundation matching your skin tone",
                },
                {
                    "name": "Foundation Brush",
                    "description": "Flat brush for foundation application",
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_generate_tutorial_structure_success(
        self, service: TutorialStructureService, sample_procedure_dict: Dict[str, Any]
    ) -> None:
        """Test successful tutorial structure generation."""
        service.ai_client.generate_structured_output.return_value = (
            sample_procedure_dict
        )

        result = await service.generate_tutorial_structure(
            style_description="Natural daytime makeup"
        )

        assert isinstance(result, MakeupProcedure)
        assert result.title == "Natural Daytime Look"
        assert len(result.steps) == 2
        assert result.steps[0].title == "Prep Your Skin"
        assert result.total_duration_minutes == 15

        # Verify AI client was called correctly
        service.ai_client.generate_structured_output.assert_called_once()
        call_args = service.ai_client.generate_structured_output.call_args
        assert call_args[1]["model"] == "gemini-2.5-flash"
        assert "Natural daytime makeup" in call_args[1]["prompt"]

    @pytest.mark.asyncio
    async def test_generate_tutorial_structure_with_gender(
        self, service: TutorialStructureService, sample_procedure_dict: Dict[str, Any]
    ) -> None:
        """Test tutorial structure generation with gender."""
        service.ai_client.generate_structured_output.return_value = (
            sample_procedure_dict
        )

        result = await service.generate_tutorial_structure(
            style_description="Bold evening look", gender="female"
        )

        assert isinstance(result, MakeupProcedure)

        # Verify gender was included in prompt
        call_args = service.ai_client.generate_structured_output.call_args
        prompt = call_args[1]["prompt"]
        assert "female" in prompt.lower() or "women" in prompt.lower()

    @pytest.mark.asyncio
    async def test_generate_tutorial_structure_with_custom_request(
        self, service: TutorialStructureService, sample_procedure_dict: Dict[str, Any]
    ) -> None:
        """Test tutorial structure generation with custom request."""
        service.ai_client.generate_structured_output.return_value = (
            sample_procedure_dict
        )
        custom_request = "Include contouring techniques"

        result = await service.generate_tutorial_structure(
            style_description="Glamorous look", custom_request=custom_request
        )

        assert isinstance(result, MakeupProcedure)

        # Verify custom request was included
        call_args = service.ai_client.generate_structured_output.call_args
        assert custom_request in call_args[1]["prompt"]

    @pytest.mark.asyncio
    async def test_generate_tutorial_structure_invalid_response(
        self, service: TutorialStructureService
    ) -> None:
        """Test handling of invalid structured response."""
        # Missing required fields
        invalid_response = {
            "title": "Test",
            "steps": [],  # Missing other required fields
        }
        service.ai_client.generate_structured_output.return_value = invalid_response

        with pytest.raises(TutorialStructureError) as exc_info:
            await service.generate_tutorial_structure(style_description="Test style")
        assert "Invalid tutorial structure" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_tutorial_structure_api_error(
        self, service: TutorialStructureService
    ) -> None:
        """Test handling of AI API errors."""
        from app.services.ai_client import AIClientAPIError

        service.ai_client.generate_structured_output.side_effect = AIClientAPIError(
            "API Error"
        )

        with pytest.raises(TutorialStructureError) as exc_info:
            await service.generate_tutorial_structure(style_description="Test style")
        assert "Failed to generate tutorial structure" in str(exc_info.value)

    def test_validate_procedure(
        self, service: TutorialStructureService, sample_procedure_dict: Dict[str, Any]
    ) -> None:
        """Test procedure validation."""
        # Valid procedure
        procedure = MakeupProcedure(**sample_procedure_dict)
        assert service.validate_procedure(procedure) is True

        # Invalid - no steps (create with at least one step then clear)
        step = MakeupStep(step_number=1, title="Test", description="Test")
        invalid_procedure = MakeupProcedure(
            title="Test",
            description="Test",
            total_duration_minutes=10,
            steps=[step],
            required_tools=[],
        )
        # Clear steps after creation to test validation
        invalid_procedure.steps = []
        assert service.validate_procedure(invalid_procedure) is False

    def test_calculate_total_duration(self, service: TutorialStructureService) -> None:
        """Test total duration calculation."""
        steps = [
            MakeupStep(
                step_number=1, title="Step 1", description="Desc", duration_seconds=60
            ),
            MakeupStep(
                step_number=2, title="Step 2", description="Desc", duration_seconds=90
            ),
            MakeupStep(
                step_number=3, title="Step 3", description="Desc", duration_seconds=30
            ),
        ]

        total_minutes = service.calculate_total_duration(steps)
        assert total_minutes == 3  # 180 seconds = 3 minutes

    def test_get_response_schema(self, service: TutorialStructureService) -> None:
        """Test response schema generation."""
        schema = service.get_response_schema()

        assert isinstance(schema, dict)
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "title" in schema["properties"]
        assert "steps" in schema["properties"]
        assert "required_tools" in schema["properties"]

        # Check nested structures
        steps_schema = schema["properties"]["steps"]
        assert steps_schema["type"] == "array"
        assert "items" in steps_schema

    @pytest.mark.asyncio
    async def test_enrich_with_details(
        self, service: TutorialStructureService, sample_procedure_dict: Dict[str, Any]
    ) -> None:
        """Test enriching procedure with additional details."""
        procedure = MakeupProcedure(**sample_procedure_dict)

        enriched = await service.enrich_with_details(procedure)

        # Should return the same procedure (enrichment is for future enhancement)
        assert enriched.title == procedure.title
        assert len(enriched.steps) == len(procedure.steps)

    def test_format_for_response(
        self, service: TutorialStructureService, sample_procedure_dict: Dict[str, Any]
    ) -> None:
        """Test formatting procedure for API response."""
        procedure = MakeupProcedure(**sample_procedure_dict)

        formatted = service.format_for_response(procedure)

        assert isinstance(formatted, dict)
        assert formatted["title"] == procedure.title
        assert formatted["description"] == procedure.description
        assert "steps" in formatted
        assert len(formatted["steps"]) == 2
        assert formatted["steps"][0]["title"] == "Prep Your Skin"
        assert "tools" in formatted
        assert len(formatted["tools"]) == 2

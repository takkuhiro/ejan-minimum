# 後で修正したい点

- Webページのタブにロゴを表示させる
- WelcomeページのUI
    - 不要なテキストの削除
    - 性別選択ボタンを見やすく。もし選択していない状態でボタンを押したらエラーのトーストを出す
    - 何分くらい処理にかかるかの目安を表示する
- スタイルページのUI
    - 戻るボタンを見やすく
⏺ localStorageに保存されているデータ:

## メモ
localStorageに保存されているデータ
  - currentTutorial: 生成されたチュートリアルデータ
  - selectedStyleId: 選択されたスタイルID
  - selectedStyle: 選択されたスタイルデータ（rawDescriptionを含む）
  - originalImageUrl: オリジナル画像のURL


/tutorialsページに遷移すると「動画読み込み中...」「画像読み込み中...」が表示されます。
動画はともかく、画像はすでに生成が完了してGoogle Cloud Storageにあるはずですよね。なのでGoogle Cloud StorageのURLをapiサーバーからのレスポンスで受け取るとすぐに表示できるはずです。

各ステップの動画のGCS URLはapiサーバからのレスポンスで受け取っていますよね。
その動画は作成中のはずなので最初は取得できないかもしれませんが、いずれ保存されるはずです。
そこで、/api/tutorials/{tutorialId}/statusをポーリングし、完了したstepの動画に関してはGoogle Cloud Storageから取得してください。

---
page_type: sample
languages:
- python
products:
- azure
- azure-cognitive-search
- azure-cognitive-services
name: ReadAPI 3.2 OCR skill for Azure Cognitive Search
urlFragment: readapi-ocr-customskill
description: This custom skill enables the OCR of the Computer Vision API of Azure Cognitive Services to be used with Azure Cognitive Serch.
---
# ReadAPI 3.2 OCR skill for Azure Cognitive Search
このカスタムスキルは、Azure Cognitive Services の Computer Vision API の OCR 機能を、Azure Cognitive Serch で使えるようにするスキルです。

# Deployment    

本スキルは、Azure Cognitive Services の Computer Vision API が必要です。また、`COMPUTER_VISION_ENDPOINT` と `COMPUTER_VISION_KEY` が必要です。Azure Functions にデプロイする際は、「アプリケーション設定」項目に設定する必要があります。

## スキルのデプロイ方法
1. Azure portal で、 Computer Vision リソースを作成します。
2. Computer Vision の API キーとエンドポイントをコピーします。
3. このレポジトリを clone します。
4. Visual Studio Code でレポジトリのフォルダを開き、Azure Functions にリモートデプロイします。
5. Functions にデプロイが完了したら, Azure Portal の Azure Functions の設定→構成から、`COMPUTER_VISION_ENDPOINT` と `COMPUTER_VISION_KEY` 環境変数にそれぞれ値を貼り付けます。


## Requirements

Azure Functions へデプロイする場合、以下が必要となります。

- [Visual Studio Code](https://azure.microsoft.com/ja-jp/products/visual-studio-code/)
- [Azure Functions for Visual Studio Code](https://docs.microsoft.com/ja-jp/azure/azure-functions/functions-develop-vs-code?tabs=csharp)

## Settings

この Funcsions は、有効な Computer Vision API キーに設定された `COMPUTER_VISION_KEY` の設定と、Computer Vision エンドポイント `COMPUTER_VISION_ENDPOINT` を必要とします。
ローカルで実行する場合は、プロジェクトのローカル環境変数で設定することができます。これにより、API キーが誤ってコードに埋め込まれることがなくなります。
Azure Functions で実行する場合、これは「アプリケーションの設定」で設定できます。


## Sample Input:

カスタムスキルは $type と url、data 項目を Azure Cognitive Search から受け取ります。data 項目には Base64 エンコードされた画像データが格納されているので、デコードして Python の バイナリストリームにロードします。

```json
{
    "values": [
        {
            "recordId": "record1",
            "data": { 
                "image": {
                    "$type": "file",
                    "url": "https://xxx.jpg",
                    "data": "/9j/4AAQS..."
                }
            }
        }
    ]
}
```

## Sample Output:

```json
{
    "values": [
        {
            "recordId": "record1",
            "ocrtext":  "吾輩は猫である。名前はまだ無い。",
            "errors": {}
        }
    ]
}
```

## スキルセット統合の例

このスキルを Azure Cognitive Search パイプラインで使用するには、スキル定義をスキルセットに追加する必要があります。この例のスキル定義の例を次に示します（特定のシナリオとスキルセット環境を反映するように入力と出力を更新する必要があります）。

```json
{
    "@odata.type": "#Microsoft.Skills.Custom.WebApiSkill",
    "name": "ReadApiSkill",
    "description": "Reads characters from a document using the Read API 3.2.",
    "uri": "[AzureFunctionEndpointUrl]/api/AnalyzeForm?code=[AzureFunctionDefaultHostKey]",
    "context": "/document/normalized_images/*",
    "inputs": [
        {
            "name": "image",
            "source": "/document/normalized_images/*"
        }
    ],
    "outputs": [
        {
          "name": "ocrtext",
          "targetName": "ocrtext"
        }
    ]
}
```


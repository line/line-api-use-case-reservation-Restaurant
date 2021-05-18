# テストデータの投入
- DynamoDB へテストデータの投入  
  本アプリの動作には店舗情報のデータを投入する必要があります。
  アプリデプロイ時に template.yaml の ShopMasterTable に設定したテーブル名のテーブルに、テストデータを投入してください。
  テストデータはbackend -> APPフォルダ内、dynamodb_data/restaurant_1.json ~ restaurant_6.json の json 形式文字列です。
  AWSマネジメントコンソールの DynamoDB コンソールにて、ペーストして投入します。(※以下画像参照)  
  
  【テストデータの投入】
  ![データの投入画像](images/test-data-charge.png)

  また、json テキストの lineAccountUrl の＠以下の部分は、作成頂いた MessagingAPI チャネルのボットのベーシック ID に変更していただく必要があります。  

  【ボットのベーシック ID 確認】
  ![ボットベーシックIDのコンソール](images/bot-basic-id.png)

[次の頁へ](validation.md)

[目次へ戻る](../README.md)
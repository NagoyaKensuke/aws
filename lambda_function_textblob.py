import json
from textblob import TextBlob

def lambda_handler(event, context):
    # 入力テキストを取得
    input_text = event.get('text', '')

    # TextBlobを使用して感情分析を行う
    blob = TextBlob(input_text)
    sentiment = blob.sentiment.polarity

    # 分析結果に基づいて感情を判定
    if sentiment > 0:
        emotion = 'positive'
    elif sentiment < 0:
        emotion = 'negative'
    else:
        emotion = 'neutral'

    # 結果を返す
    return {
        'statusCode': 200,
        'body': json.dumps({
            'text': input_text,
            'sentiment': emotion
        })
    }

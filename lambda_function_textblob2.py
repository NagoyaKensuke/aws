import json
import logging
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from janome.tokenizer import Tokenizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ロギングの設定
logging.basicConfig(level=logging.INFO)

def lambda_handler(event, context):
    try:
        # 入力テキストを取得
        input_text = event.get('text')
        if not input_text:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'text parameter is required'
                })
            }

        # 日本語か英語か判定する
        lang = TextBlob(input_text).detect_language()

        # 日本語の場合
        if lang == 'ja':
            # Janomeを使用して形態素解析と感情分析を行う
            tokenizer = Tokenizer()
            tokens = tokenizer.tokenize(input_text)
            words = [token.surface for token in tokens if token.part_of_speech.startswith('名詞') or token.part_of_speech.startswith('形容詞')]
            blob = TextBlob(' '.join(words), analyzer=NaiveBayesAnalyzer())
            sentiment = blob.sentiment.p_pos - blob.sentiment.p_neg
            subjectivity = blob.sentiment.p_pos + blob.sentiment.p_neg

            # 分析結果に基づいて感情を判定
            if sentiment > 0:
                emotion = 'positive'
            elif sentiment < 0:
                emotion = 'negative'
            else:
                emotion = 'neutral'

            # ログ出力
            logging.info(f"Sentiment analysis for text: {input_text}, Result: {emotion}")

            # 結果を返す
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'text': input_text,
                    'sentiment': emotion,
                    'sentiment_score': sentiment,
                    'subjectivity': subjectivity,
                    'library': 'Janome',
                    'class': 'NaiveBayesAnalyzer'
                })
            }

        # 英語の場合
        elif lang == 'en':
            # TextBlobを使用して感情分析を行う
            blob = TextBlob(input_text)
            sentiment_tb = blob.sentiment.polarity
            subjectivity_tb = blob.sentiment.subjectivity

            # 分析結果に基づいて感情を判定
            if sentiment_tb > 0:
                emotion_tb = 'positive'
            elif sentiment_tb < 0:
                emotion_tb = 'negative'
            else:
                emotion_tb = 'neutral'

            # VADERを使用して感情分析を行う
            sia = SentimentIntensityAnalyzer()
            sentiment_vd = sia.polarity_scores(input_text)
            emotion_vd = sentiment_vd['compound']

            # ログ出力
            logging.info(f"Sentiment analysis for text: {input_text}, Result: {emotion_tb} (TextBlob), {emotion_vd} (VADER)")

            # 結果を返す
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'text': input_text,
                    'sentiment': emotion_tb,
                    'sentiment_score': sentiment_tb,
                    'subjectivity': subjectivity_tb,
                    'library': 'TextBlob',
                    'class': 'PatternAnalyzer',
                    'sentiment_vader': emotion_vd,
                    'sentiment_score_vader': sentiment_vd,
                    'library_vader': 'VADER',
                    'class_vader': 'SentimentIntensityAnalyzer'
                })
            }

        # その他の言語の場合
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f'unsupported language: {lang}'
                })
            }

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal Server Error'
            })
        }

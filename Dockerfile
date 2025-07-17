FROM python:3.12-alpine

RUN addgroup -S -g 1337 lovelace_bot && adduser -S -u 1337 lovelace_bot -G lovelace_bot

USER lovelace_bot:lovelace_bot

WORKDIR /lovelace_bot_app

COPY --chown=lovelace_bot:lovelace_bot . /lovelace_bot_app

RUN pip install --no-cache-dir -r requirements.txt

ENV ENV=PROD

CMD ["python", "bot.py"]

# Deploy to Heroku

```
heroku stack:set container --app chat-db-rag
heroku container:push web --app chat-db-rag
heroku container:release web --app chat-db-rag
```
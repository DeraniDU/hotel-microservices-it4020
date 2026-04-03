const express = require('express');
const swaggerUi = require('swagger-ui-express');
const app = express();
const doc = { openapi: "3.0.0", info: { title: "Test", version: "1.0" }, paths: {} };

app.use('/restaurant', swaggerUi.serve);
app.get('/restaurant', swaggerUi.setup(doc));

app.listen(3334, () => console.log('test2 running on 3334'));

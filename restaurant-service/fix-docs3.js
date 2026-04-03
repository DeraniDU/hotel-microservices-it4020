const express = require('express');
const swaggerUi = require('swagger-ui-express');
const app = express();
const doc = { openapi: "3.0.0", info: { title: "Test", version: "1.0" }, paths: {} };

app.get('/restaurant', (req, res, next) => {
    if (!req.originalUrl.endsWith('/')) {
        return res.redirect(301, req.originalUrl + '/');
    }
    next();
});
app.use('/restaurant', swaggerUi.serve, swaggerUi.setup(doc));

app.listen(3335, () => console.log('test3 running on 3335'));

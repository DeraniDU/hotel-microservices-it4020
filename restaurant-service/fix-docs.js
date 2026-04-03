const express = require('express');
const swaggerUi = require('swagger-ui-express');
const app = express();
const doc = { openapi: "3.0.0", info: { title: "Test", version: "1.0" }, paths: {} };

app.get('/restaurant', (req, res) => {
   res.redirect('/restaurant/docs');
});
app.use('/restaurant/docs', swaggerUi.serve, swaggerUi.setup(doc));

app.listen(3333, () => console.log('test running on 3333'));

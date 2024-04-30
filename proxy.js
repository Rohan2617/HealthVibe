const express = require('express');
const cors = require('cors');
const fetch = require('node-fetch');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());

app.get('/pdf/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const response = await fetch(`https://api.ods.od.nih.gov/dsld/s3/pdf/${id}.pdf`);
    const pdfBuffer = await response.buffer();
    res.setHeader('Content-Type', 'application/pdf');
    res.send(pdfBuffer);
  } catch (error) {
    console.error(error);
    res.status(500).send('Internal Server Error');
  }
});

app.listen(PORT, () => {
  console.log(`Proxy server is running on port ${PORT}`);
});

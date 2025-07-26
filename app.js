const express = require('express');
const AWS = require('aws-sdk');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

// Replace this with your actual queue URL
const queueUrl = 'https://sqs.<region>.amazonaws.com/<account-id>/screenshot-requests';

// Configure AWS SDK (region should match your queue)
AWS.config.update({ region: 'your-region' });

const sqs = new AWS.SQS();

app.post('/screenshot', (req, res) => {
    const { url } = req.body;

    if (!url) {
        return res.status(400).json({ error: 'URL is required' });
    }

    const params = {
        MessageBody: JSON.stringify({ url }),
        QueueUrl: queueUrl,
    };

    sqs.sendMessage(params, (err, data) => {
        if (err) {
            console.error('Error sending message:', err);
            res.status(500).json({ error: 'Failed to enqueue URL' });
        } else {
            console.log('Message sent:', data.MessageId);
            res.status(200).json({ message: 'URL enqueued successfully', id: data.MessageId });
        }
    });
});

const PORT = 80;
app.listen(PORT, () => {
    console.log(`App server listening on port ${PORT}`);
});

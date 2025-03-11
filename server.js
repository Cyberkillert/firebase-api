const express = require("express");
const admin = require("firebase-admin");

const app = express();
const PORT = process.env.PORT || 3000;

// Initialize Firebase Admin SDK
if (!admin.apps.length) {
    admin.initializeApp({
        credential: admin.credential.cert({
            "type": "service_account",
            "project_id": "store-bazaar-39fbf",
            "private_key_id": "your_private_key_id",
            "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
            "client_email": "your_service_account_email",
            "client_id": "your_client_id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "your_client_cert_url"
        }),
        databaseURL: "https://store-bazaar-39fbf-default-rtdb.firebaseio.com",
    });
}

const db = admin.database();

// ✅ Fetch all orders
app.get("/orders", async (req, res) => {
    try {
        const ref = db.ref("order"); // ✅ Only fetch "order" data
        const snapshot = await ref.once("value");

        if (snapshot.exists()) {
            res.json(snapshot.val()); // ✅ Return all orders
        } else {
            res.status(404).json({ message: "No orders found" });
        }
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ✅ Fetch a specific order by its unique ID
app.get("/order/:id", async (req, res) => {
    try {
        const orderId = req.params.id;
        const ref = db.ref(`order/${orderId}`); // ✅ Fetch a single order
        const snapshot = await ref.once("value");

        if (snapshot.exists()) {
            res.json(snapshot.val()); // ✅ Return the specific order
        } else {
            res.status(404).json({ message: "Order not found" });
        }
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

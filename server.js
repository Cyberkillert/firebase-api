const express = require("express");
const admin = require("firebase-admin");

const app = express();
const PORT = process.env.PORT || 3000;

admin.initializeApp({
    credential: admin.credential.applicationDefault(),
    databaseURL: "https://android-e312a-default-rtdb.firebaseio.com", // Replace with your database URL
});

const db = admin.database();

app.get("/update", async (req, res) => {
    try {
        const ref = db.ref("/");
        const snapshot = await ref.once("value");
        res.json(snapshot.val() || { message: "No data available" });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

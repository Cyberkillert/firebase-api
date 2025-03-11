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
  "private_key_id": "b05117e63d4451abe2300b84d7a3580bf3191f44",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDaF0prvfhpXl7r\nxB1Awv7VE6aGZnm3sDnfRMaE9qNwMJ4tiMb3OkwouMjUsSxUx6C6tiqA4hCXpl9i\nhTb/RTwUkMjpaFK7hxfO2l8Ro8b9iLVc6PhgqGwKt3nAHecpA7zYQXIcRFf+SlKr\nQSHiiuWcEXPUta85zRaou1KNe8lKS2SU4Cdxv7zVVCe39sVwOgbg9SFaiJOXZ5XR\nKWr+QUilf2dsLfg4DeLWjtn5QLYo7ICyEmjUmBd8A/RwKe4fF6JSveIitKxe3hau\nmCixgrQJzcTnR3F/hA3m+4KmqK2MHSubUtwiZq6s8V7pOOVSAFBImz//WvyGvxEs\nv2Ux42YZAgMBAAECggEAF3Z2P5NhXl+kXV+8yG76CL0rlw2/BkmnnjspUtxwbqVS\nXSJ4Cli7oQ1pMMWrV+cepfurZLB9eb0wyZn8ldeyXCGL9d1u+iURZQQGApEwuy26\nGkfnkcmIzxnYV7h32iggaNEYqE0bfNxs2qcAEN3h0CmqAR43PuQPLiGyAs3olM0H\nCAqcB/nVDJNspTTg1nKYCxZFvch3FerRDNqSv5JueLfS205pSSlFRs4jLN/WOYbW\ng4xG+v+bepoqfpWZjOVTcVT4vUaerSFLZEUdFaBJmLhbJDUndRbU2xlEFQW8fv2W\n0m40Lj9ewdxPZvpKGwCpdOhvajrj/C7JTFUr7eF+AQKBgQDxD452eO/bNEnKS+4J\nLTRqYvkNjQKcPiF2oEv7QNqPGSTZG0h0Ucbbnx3NfwHhd2eUlVXjl3SVtD9eOCUV\nPIqWFmzAwXireNiL5Yc9Xz/ETUaAqvqLhzLC9L+m7MF/T8nc+OUQgUC0eok1tNzH\nvwYpPTScaWGmAp+CVIy1qniCAQKBgQDnm1EwfXCHZoClhHy9k0MsWtOFptZ7NWLc\niQgvugScuQHmkH/5Zr/rtJCiM3z3HC7o5Nwy6qtHtwPkbGsR4YQgUC5TZl49bORS\nw1jlz9TGxU2gctf7fzCaakoDHrB54/b7CF1xfpuTsp/irqw8riGJFJT4kdr+feLu\nl1VWZLa0GQKBgQCjIjL36+nuP1l8hJwHK8dgA7Clwfq1P7qnq90foIkH9C0im7sR\ntNHNiMXDbqMYMRUw0Ur5pWJpeTy1B2vZDkp/PZfFbmi6KiLpsaAvIUlnECCZLJw3\nVnw8wSL91RUxkg568xkZbU8blB1M8iPDLXv+5oO3If3KOdY2ff9nZYD+AQKBgBLo\nJPqWYudKwNnCNQSszuECER5p/jxUoVtrfFWZE+NPXw5ZYXkUoDo3pU74cQ0jKdkt\nRaSKb60NDa5KA3uUM1sH8KAyTSMqjoELHWi1TKNlW+7rMSKAwZD5eE1E5hctOu5H\nQomPUlf+TvsMU1cox+gO3BJmpb/8utfLVtYUpq2RAoGBAOXuMAyOR295RIGfscMU\nn4FXKNfnG15PpicrOC3lYWITFNdnG72hrSTtRbSxQwo/PaLeT+AaTCUJwUe+ehHF\nGYAjcExf0CycVj+4Mwxw7gZigNpCTOPGDBwIC0BQdOFHktVoXwpS3TKJFo+tDqCe\n91hWWUvunwXNY4firL8/qhjt\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-pelx0@store-bazaar-39fbf.iam.gserviceaccount.com",
  "client_id": "116562458796825020947",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-pelx0%40store-bazaar-39fbf.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
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

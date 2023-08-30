import { MongoClient } from "mongodb";
import nextConnect from 'next-connect';

const client = new MongoClient(
    "mongodb+srv://Woohun:wfv4zVSkgudg373s@cluster0.xzrabhp.mongodb.net/?retryWrites=true&w=majority",
    {
        useNewUrlParser: true,
        useUnifiedTopology: true,
});

async function db(req, res, next) {
    req.dbClient = client;
    req.db = client.db('MLB Tracker');
    return next();
}

const middleware = nextConnect();

middleware.use(db);

export default middleware;

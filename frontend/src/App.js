import React, { useEffect, useState } from 'react';
import axios from 'axios';

const NewsList = () => {
    const [articles, setArticles] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchArticles = async () => {
            try {
                const response = await axios.get('/records');
                setArticles(response.data);
            } catch (err) {
                setError(err.message);
            }
        };

        fetchArticles();
    }, []);

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <div>
            <h1>News Articles</h1>
            <ul>
                {articles.map((article) => (
                    <li><a href = {article.link}>{article.title}</a></li>
                ))}
            </ul>
        </div>
    );
};

export default NewsList;

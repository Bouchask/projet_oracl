import { Link } from 'react-router-dom';

const Home = () => {
    return (
        <div className="container">
            <div className="header">
                <h1>Welcome to the Course Registration System</h1>
            </div>
            <div style={{ textAlign: 'center', marginTop: '20px' }}>
                <Link to="/login">
                    <button className="btn btn-primary">Login</button>
                </Link>
            </div>
        </div>
    );
};

export default Home;

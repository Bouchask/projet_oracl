import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import StudentDashboard from './pages/StudentDashboard';
import TeacherDashboard from './pages/TeacherDashboard';
import AdminDashboard from './pages/AdminDashboard';

const PrivateRoute = ({ children, role, userRole }) => {
    const isAuthenticated = !!localStorage.getItem('token');
    if (!isAuthenticated) {
        return <Navigate to="/login" />;
    }
    if (role && role !== userRole) {
        return <Navigate to="/" />;
    }
    return children;
};

const App = () => {
    const token = localStorage.getItem('token');
    let userRole = null;
    if (token) {
        const payload = JSON.parse(atob(token.split('.')[1]));
        userRole = payload.role;
    }

    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<Login />} />
                <Route 
                    path="/student" 
                    element={
                        <PrivateRoute userRole={userRole} role="student">
                            <StudentDashboard />
                        </PrivateRoute>
                    } 
                />
                <Route 
                    path="/teacher" 
                    element={
                        <PrivateRoute userRole={userRole} role="teacher">
                            <TeacherDashboard />
                        </PrivateRoute>
                    } 
                />
                <Route 
                    path="/admin" 
                    element={
                        <PrivateRoute userRole={userRole} role="admin">
                            <AdminDashboard />
                        </PrivateRoute>
                    } 
                />
            </Routes>
        </Router>
    );
};

export default App;
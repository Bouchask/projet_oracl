import { useState, useEffect } from 'react';
import axios from 'axios';

const StudentDashboard = () => {
    const [courses, setCourses] = useState([]);
    const [sections, setSections] = useState([]);
    const [grades, setGrades] = useState([]);
    const [message, setMessage] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            const token = localStorage.getItem('token');
            const config = { headers: { 'x-access-token': token } };

            try {
                const coursesRes = await axios.get(`${import.meta.env.VITE_API_URL}/courses`, config);
                setCourses(coursesRes.data);

                const sectionsRes = await axios.get(`${import.meta.env.VITE_API_URL}/sections`, config);
                setSections(sectionsRes.data);

                const gradesRes = await axios.get(`${import.meta.env.VITE_API_URL}/grades`, config);
                setGrades(gradesRes.data);
            } catch (error) {
                setMessage('Error fetching data');
            }
        };
        fetchData();
    }, []);

    const handleRegister = async (sectionId) => {
        try {
            const token = localStorage.getItem('token');
            const payload = JSON.parse(atob(token.split('.')[1]));
            const studentId = payload.user; // Assuming username is the student_id
            const config = { headers: { 'x-access-token': token } };
            await axios.post(`${import.meta.env.VITE_API_URL}/registration`, { section_id: sectionId, student_id: studentId }, config);
            setMessage('Registration successful!');
        } catch (error) {
            setMessage(error.response.data.message);
        }
    };

    return (
        <div className="container">
            <div className="header">
                <h2>Student Dashboard</h2>
            </div>
            {message && <div className="alert alert-info">{message}</div>}
            <div className="dashboard">
                <div className="dashboard-card">
                    <h3>Courses</h3>
                    <ul className="list-group">
                        {courses.map(course => (
                            <li key={course.course_code} className="list-group-item">{course.title} ({course.course_code})</li>
                        ))}
                    </ul>
                </div>
                <div className="dashboard-card">
                    <h3>Sections</h3>
                    <ul className="list-group">
                        {sections.map(section => (
                            <li key={section.section_id} className="list-group-item">
                                {section.course_code} - Section {section.section_id}
                                <button onClick={() => handleRegister(section.section_id)} className="btn btn-primary float-right">Register</button>
                            </li>
                        ))}
                    </ul>
                </div>
                <div className="dashboard-card">
                    <h3>My Grades</h3>
                    <ul className="list-group">
                        {grades.map(grade => (
                            <li key={grade.course_code} className="list-group-item">
                                {grade.course_code}: {grade.grade} ({grade.status})
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default StudentDashboard;

import { useState, useEffect } from 'react';
import axios from 'axios';

const TeacherDashboard = () => {
    const [sections, setSections] = useState([]);
    const [students, setStudents] = useState([]);
    const [message, setMessage] = useState('');
    const [gradeData, setGradeData] = useState({ student_id: '', course_code: '', grade: '', status: '' });

    useEffect(() => {
        const fetchData = async () => {
            const token = localStorage.getItem('token');
            const config = { headers: { 'x-access-token': token } };
            try {
                const sectionsRes = await axios.get(`${import.meta.env.VITE_API_URL}/sections`, config);
                setSections(sectionsRes.data);

                const studentsRes = await axios.get(`${import.meta.env.VITE_API_URL}/students`, config);
                setStudents(studentsRes.data);
            } catch (error) {
                setMessage('Error fetching data');
            }
        };
        fetchData();
    }, []);

    const handleGradeSubmit = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        const config = { headers: { 'x-access-token': token } };
        try {
            await axios.post(`${import.meta.env.VITE_API_URL}/grades`, gradeData, config);
            setMessage('Grade submitted successfully!');
        } catch (error) {
            setMessage(error.response.data.message);
        }
    };

    const handleInputChange = (e) => {
        setGradeData({ ...gradeData, [e.target.name]: e.target.value });
    };

    return (
        <div className="container">
            <div className="header">
                <h2>Teacher Dashboard</h2>
            </div>
            {message && <div className="alert alert-info">{message}</div>}
            <div className="dashboard">
                <div className="dashboard-card">
                    <h3>My Sections</h3>
                    <ul className="list-group">
                        {sections.map(section => (
                            <li key={section.section_id} className="list-group-item">{section.course_code} - Section {section.section_id}</li>
                        ))}
                    </ul>
                </div>
                <div className="dashboard-card">
                    <h3>Students</h3>
                    <ul className="list-group">
                        {students.map(student => (
                            <li key={student.student_id} className="list-group-item">{student.first_name} {student.last_name} ({student.email})</li>
                        ))}
                    </ul>
                </div>
                <div className="dashboard-card">
                    <h3>Submit Grade</h3>
                    <form onSubmit={handleGradeSubmit}>
                        <div className="form-group">
                            <input name="student_id" className="form-control" placeholder="Student ID" onChange={handleInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="course_code" className="form-control" placeholder="Course Code" onChange={handleInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="grade" className="form-control" placeholder="Grade" onChange={handleInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="status" className="form-control" placeholder="Status" onChange={handleInputChange} />
                        </div>
                        <button type="submit" className="btn btn-primary">Submit Grade</button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default TeacherDashboard;

import { useState, useEffect } from 'react';
import axios from 'axios';

const AdminDashboard = () => {
    const [sectionCapacity, setSectionCapacity] = useState([]);
    const [registrationDetails, setRegistrationDetails] = useState([]);
    const [teachers, setTeachers] = useState([]);
    const [courses, setCourses] = useState([]);
    const [sections, setSections] = useState([]);
    const [students, setStudents] = useState([]);
    const [message, setMessage] = useState('');
    const [courseData, setCourseData] = useState({ course_code: '', title: '', credits: '', departement_id: '' });
    const [sectionData, setSectionData] = useState({ section_id: '', course_code: '', semester_id: '', instructor_id: '', max_capacity: '', day_of_week: '', start_time: '', end_time: '', room_location: '' });
    const [teacherData, setTeacherData] = useState({ instructor_id: '', first_name: '', last_name: '', email: '' });
    const [studentData, setStudentData] = useState({ student_id: '', first_name: '', last_name: '', email: '', phone_number: '' });
    const [editingCourse, setEditingCourse] = useState(null);
    const [editingSection, setEditingSection] = useState(null);
    const [editingTeacher, setEditingTeacher] = useState(null);
    const [editingStudent, setEditingStudent] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            const token = localStorage.getItem('token');
            const config = { headers: { 'x-access-token': token } };

            try {
                const capacityRes = await axios.get(`${import.meta.env.VITE_API_URL}/views/section-capacity`, config);
                setSectionCapacity(capacityRes.data);

                const registrationRes = await axios.get(`${import.meta.env.VITE_API_URL}/views/registration-details`, config);
                setRegistrationDetails(registrationRes.data);

                const teachersRes = await axios.get(`${import.meta.env.VITE_API_URL}/teachers`, config);
                setTeachers(teachersRes.data);

                const coursesRes = await axios.get(`${import.meta.env.VITE_API_URL}/courses`, config);
                setCourses(coursesRes.data);

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

    const handleCourseInputChange = (e) => {
        setCourseData({ ...courseData, [e.target.name]: e.target.value });
    };

    const handleCourseSubmit = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        const config = { headers: { 'x-access-token': token } };
        try {
            await axios.post(`${import.meta.env.VITE_API_URL}/courses`, courseData, config);
            setMessage('Course added successfully!');
        } catch (error) {
            setMessage(error.response.data.message);
        }
    };

    const handleSectionInputChange = (e) => {
        setSectionData({ ...sectionData, [e.target.name]: e.target.value });
    };

    const handleSectionSubmit = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        const config = { headers: { 'x-access-token': token } };
        try {
            await axios.post(`${import.meta.env.VITE_API_URL}/sections`, sectionData, config);
            setMessage('Section added successfully!');
        } catch (error) {
            setMessage(error.response.data.message);
        }
    };

    const handleTeacherInputChange = (e) => {
        setTeacherData({ ...teacherData, [e.target.name]: e.target.value });
    };

    const handleTeacherSubmit = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        const config = { headers: { 'x-access-token': token } };
        try {
            await axios.post(`${import.meta.env.VITE_API_URL}/teachers`, teacherData, config);
            setMessage('Teacher added successfully!');
        } catch (error) {
            setMessage(error.response.data.message);
        }
    };

    const handleStudentInputChange = (e) => {
        setStudentData({ ...studentData, [e.target.name]: e.target.value });
    };

    const handleStudentSubmit = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        const config = { headers: { 'x-access-token': token } };
        try {
            await axios.post(`${import.meta.env.VITE_API_URL}/students`, studentData, config);
            setMessage('Student added successfully!');
        } catch (error) {
            setMessage(error.response.data.message);
        }
    };

    const handleDeleteCourse = async (course_code) => {
        const token = localStorage.getItem('token');
        const config = { 
            headers: { 'x-access-token': token },
            data: { course_code: course_code }
        };
        try {
            await axios.delete(`${import.meta.env.VITE_API_URL}/courses`, config);
            setMessage('Course deleted successfully!');
        } catch (error) {
            setMessage(error.response.data.message);
        }
    };

    const handleDeleteSection = async (section_id) => {
        const token = localStorage.getItem('token');
        const config = { 
            headers: { 'x-access-token': token },
            data: { section_id: section_id }
        };
        try {
            await axios.delete(`${import.meta.env.VITE_API_URL}/sections`, config);
            setMessage('Section deleted successfully!');
        } catch (error) {
            setMessage(error.response.data.message);
        }
    };

    const handleDeleteTeacher = async (instructor_id) => {
        const token = localStorage.getItem('token');
        const config = { 
            headers: { 'x-access-token': token },
            data: { instructor_id: instructor_id }
        };
        try {
            await axios.delete(`${import.meta.env.VITE_API_URL}/teachers`, config);
            setMessage('Teacher deleted successfully!');
        } catch (error) {
            setMessage(error.response.data.message);
        }
    };

    const handleDeleteStudent = async (student_id) => {
        const token = localStorage.getItem('token');
        const config = { 
            headers: { 'x-access-token': token },
            data: { student_id: student_id }
        };
        try {
            await axios.delete(`${import.meta.env.VITE_API_URL}/students`, config);
            setMessage('Student deleted successfully!');
        } catch (error) {
            setMessage(error.response.data.message);
        }
    };

    const handleUpdateCourse = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        const config = { headers: { 'x-access-token': token } };
        try {
            await axios.put(`${import.meta.env.VITE_API_URL}/courses`, editingCourse, config);
            setEditingCourse(null);
            setMessage('Course updated successfully!');
        } catch (error) {
            setMessage(error.response.data.message);
        }
    };

    const handleUpdateSection = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        const config = { headers: { 'x-access-token': token } };
        try {
            await axios.put(`${import.meta.env.VITE_API_URL}/sections`, editingSection, config);
            setEditingSection(null);
            setMessage('Section updated successfully!');
        } catch (error) {
            setMessage(error.response.data.message);
        }
    };

    const handleUpdateTeacher = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        const config = { headers: { 'x-access-token': token } };
        try {
            await axios.put(`${import.meta.env.VITE_API_URL}/teachers`, editingTeacher, config);
            setEditingTeacher(null);
            setMessage('Teacher updated successfully!');
        } catch (error) {
            setMessage(error.response.data.message);
        }
    };

    const handleUpdateStudent = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        const config = { headers: { 'x-access-token': token } };
        try {
            await axios.put(`${import.meta.env.VITE_API_URL}/students`, editingStudent, config);
            setEditingStudent(null);
            setMessage('Student updated successfully!');
        } catch (error) {
            setMessage(error.response.data.message);
        }
    };

    return (
        <div className="container">
            <div className="header">
                <h2>Admin Dashboard</h2>
            </div>
            {message && <div className="alert alert-info">{message}</div>}
            <div className="dashboard">
                <div className="dashboard-card">
                    <h3>Add Course</h3>
                    <form onSubmit={handleCourseSubmit}>
                        <div className="form-group">
                            <input name="course_code" className="form-control" placeholder="Course Code" onChange={handleCourseInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="title" className="form-control" placeholder="Title" onChange={handleCourseInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="credits" className="form-control" placeholder="Credits" onChange={handleCourseInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="departement_id" className="form-control" placeholder="Department ID" onChange={handleCourseInputChange} />
                        </div>
                        <button type="submit" className="btn btn-primary">Add Course</button>
                    </form>
                </div>
                <div className="dashboard-card">
                    <h3>Add Section</h3>
                    <form onSubmit={handleSectionSubmit}>
                        <div className="form-group">
                            <input name="section_id" className="form-control" placeholder="Section ID" onChange={handleSectionInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="course_code" className="form-control" placeholder="Course Code" onChange={handleSectionInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="semester_id" className="form-control" placeholder="Semester ID" onChange={handleSectionInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="instructor_id" className="form-control" placeholder="Instructor ID" onChange={handleSectionInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="max_capacity" className="form-control" placeholder="Max Capacity" onChange={handleSectionInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="day_of_week" className="form-control" placeholder="Day of Week" onChange={handleSectionInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="start_time" className="form-control" placeholder="Start Time (HH:MI)" onChange={handleSectionInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="end_time" className="form-control" placeholder="End Time (HH:MI)" onChange={handleSectionInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="room_location" className="form-control" placeholder="Room Location" onChange={handleSectionInputChange} />
                        </div>
                        <button type="submit" className="btn btn-primary">Add Section</button>
                    </form>
                </div>
                <div className="dashboard-card">
                    <h3>Add Teacher</h3>
                    <form onSubmit={handleTeacherSubmit}>
                        <div className="form-group">
                            <input name="instructor_id" className="form-control" placeholder="Instructor ID" onChange={handleTeacherInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="first_name" className="form-control" placeholder="First Name" onChange={handleTeacherInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="last_name" className="form-control" placeholder="Last Name" onChange={handleTeacherInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="email" className="form-control" placeholder="Email" onChange={handleTeacherInputChange} />
                        </div>
                        <button type="submit" className="btn btn-primary">Add Teacher</button>
                    </form>
                </div>
                <div className="dashboard-card">
                    <h3>Add Student</h3>
                    <form onSubmit={handleStudentSubmit}>
                        <div className="form-group">
                            <input name="student_id" className="form-control" placeholder="Student ID" onChange={handleStudentInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="first_name" className="form-control" placeholder="First Name" onChange={handleStudentInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="last_name" className="form-control" placeholder="Last Name" onChange={handleStudentInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="email" className="form-control" placeholder="Email" onChange={handleStudentInputChange} />
                        </div>
                        <div className="form-group">
                            <input name="phone_number" className="form-control" placeholder="Phone Number" onChange={handleStudentInputChange} />
                        </div>
                        <button type="submit" className="btn btn-primary">Add Student</button>
                    </form>
                </div>
                {editingCourse && (
                    <div className="dashboard-card">
                        <h3>Edit Course</h3>
                        <form onSubmit={handleUpdateCourse}>
                            <div className="form-group">
                                <input name="title" className="form-control" value={editingCourse.title} onChange={(e) => setEditingCourse({...editingCourse, title: e.target.value})} />
                            </div>
                            <div className="form-group">
                                <input name="credits" className="form-control" value={editingCourse.credits} onChange={(e) => setEditingCourse({...editingCourse, credits: e.target.value})} />
                            </div>
                            <div className="form-group">
                                <input name="departement_id" className="form-control" value={editingCourse.departement_id} onChange={(e) => setEditingCourse({...editingCourse, departement_id: e.target.value})} />
                            </div>
                            <button type="submit" className="btn btn-primary">Save</button>
                            <button onClick={() => setEditingCourse(null)} className="btn btn-secondary">Cancel</button>
                        </form>
                    </div>
                )}
                {editingSection && (
                    <div className="dashboard-card">
                        <h3>Edit Section</h3>
                        <form onSubmit={handleUpdateSection}>
                            <div className="form-group">
                                <input name="course_code" className="form-control" value={editingSection.course_code} onChange={(e) => setEditingSection({...editingSection, course_code: e.target.value})} />
                            </div>
                            <div className="form-group">
                                <input name="semester_id" className="form-control" value={editingSection.semester_id} onChange={(e) => setEditingSection({...editingSection, semester_id: e.target.value})} />
                            </div>
                            <div className="form-group">
                                <input name="instructor_id" className="form-control" value={editingSection.instructor_id} onChange={(e) => setEditingSection({...editingSection, instructor_id: e.target.value})} />
                            </div>
                            <div className="form-group">
                                <input name="max_capacity" className="form-control" value={editingSection.max_capacity} onChange={(e) => setEditingSection({...editingSection, max_capacity: e.target.value})} />
                            </div>
                            <div className="form-group">
                                <input name="day_of_week" className="form-control" value={editingSection.day_of_week} onChange={(e) => setEditingSection({...editingSection, day_of_week: e.target.value})} />
                            </div>
                            <div className="form-group">
                                <input name="start_time" className="form-control" value={editingSection.start_time} onChange={(e) => setEditingSection({...editingSection, start_time: e.target.value})} />
                            </div>
                            <div className="form-group">
                                <input name="end_time" className="form-control" value={editingSection.end_time} onChange={(e) => setEditingSection({...editingSection, end_time: e.target.value})} />
                            </div>
                            <div className="form-group">
                                <input name="room_location" className="form-control" value={editingSection.room_location} onChange={(e) => setEditingSection({...editingSection, room_location: e.target.value})} />
                            </div>
                            <button type="submit" className="btn btn-primary">Save</button>
                            <button onClick={() => setEditingSection(null)} className="btn btn-secondary">Cancel</button>
                        </form>
                    </div>
                )}
                {editingTeacher && (
                    <div className="dashboard-card">
                        <h3>Edit Teacher</h3>
                        <form onSubmit={handleUpdateTeacher}>
                            <div className="form-group">
                                <input name="first_name" className="form-control" value={editingTeacher.first_name} onChange={(e) => setEditingTeacher({...editingTeacher, first_name: e.target.value})} />
                            </div>
                            <div className="form-group">
                                <input name="last_name" className="form-control" value={editingTeacher.last_name} onChange={(e) => setEditingTeacher({...editingTeacher, last_name: e.target.value})} />
                            </div>
                            <div className="form-group">
                                <input name="email" className="form-control" value={editingTeacher.email} onChange={(e) => setEditingTeacher({...editingTeacher, email: e.target.value})} />
                            </div>
                            <button type="submit" className="btn btn-primary">Save</button>
                            <button onClick={() => setEditingTeacher(null)} className="btn btn-secondary">Cancel</button>
                        </form>
                    </div>
                )}
                {editingStudent && (
                    <div className="dashboard-card">
                        <h3>Edit Student</h3>
                        <form onSubmit={handleUpdateStudent}>
                            <div className="form-group">
                                <input name="first_name" className="form-control" value={editingStudent.first_name} onChange={(e) => setEditingStudent({...editingStudent, first_name: e.target.value})} />
                            </div>
                            <div className="form-group">
                                <input name="last_name" className="form-control" value={editingStudent.last_name} onChange={(e) => setEditingStudent({...editingStudent, last_name: e.target.value})} />
                            </div>
                            <div className="form-group">
                                <input name="email" className="form-control" value={editingStudent.email} onChange={(e) => setEditingStudent({...editingStudent, email: e.target.value})} />
                            </div>
                            <div className="form-group">
                                <input name="phone_number" className="form-control" value={editingStudent.phone_number} onChange={(e) => setEditingStudent({...editingStudent, phone_number: e.target.value})} />
                            </div>
                            <button type="submit" className="btn btn-primary">Save</button>
                            <button onClick={() => setEditingStudent(null)} className="btn btn-secondary">Cancel</button>
                        </form>
                    </div>
                )}
                <div className="dashboard-card">
                    <h3>Section Capacity</h3>
                    <ul className="list-group">
                        {sectionCapacity.map(item => (
                            <li key={item.section_id} className="list-group-item">
                                {item.course_title} (Section {item.section_id}): {item.current_enrolled}/{item.max_capacity}
                            </li>
                        ))}
                    </ul>
                </div>
                <div className="dashboard-card">
                    <h3>Registration Details</h3>
                    <ul className="list-group">
                        {registrationDetails.map(item => (
                            <li key={item.registration_id} className="list-group-item">
                                {item.first_name} {item.last_name} registered for {item.course_title} on {item.registration_date}
                            </li>
                        ))}
                    </ul>
                </div>
                <div className="dashboard-card">
                    <h3>Teachers</h3>
                    <ul className="list-group">
                        {teachers.map(teacher => (
                            <li key={teacher.instructor_id} className="list-group-item">
                                {teacher.first_name} {teacher.last_name} ({teacher.email})
                                <button onClick={() => setEditingTeacher(teacher)} className="btn btn-secondary float-right">Update</button>
                                <button onClick={() => handleDeleteTeacher(teacher.instructor_id)} className="btn btn-danger float-right">Delete</button>
                            </li>
                        ))}
                    </ul>
                </div>
                <div className="dashboard-card">
                    <h3>Courses</h3>
                    <ul className="list-group">
                        {courses.map(course => (
                            <li key={course.course_code} className="list-group-item">
                                {course.title} ({course.course_code})
                                <button onClick={() => setEditingCourse(course)} className="btn btn-secondary float-right">Update</button>
                                <button onClick={() => handleDeleteCourse(course.course_code)} className="btn btn-danger float-right">Delete</button>
                            </li>
                        ))}
                    </ul>
                </div>
                <div className="dashboard-card">
                    <h3>Sections</h3>
                    <ul className="list-group">
                        {sections.map(section => (
                            <li key={section.section_id} className="list-group-item">
                                {section.course_code} - Section {section.section_id}
                                <button onClick={() => setEditingSection(section)} className="btn btn-secondary float-right">Update</button>
                                <button onClick={() => handleDeleteSection(section.section_id)} className="btn btn-danger float-right">Delete</button>
                            </li>
                        ))}
                    </ul>
                </div>
                <div className="dashboard-card">
                    <h3>Students</h3>
                    <ul className="list-group">
                        {students.map(student => (
                            <li key={student.student_id} className="list-group-item">
                                {student.first_name} {student.last_name} ({student.email})
                                <button onClick={() => setEditingStudent(student)} className="btn btn-secondary float-right">Update</button>
                                <button onClick={() => handleDeleteStudent(student.student_id)} className="btn btn-danger float-right">Delete</button>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
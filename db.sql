CREATE TABLE IF NOT EXISTS student (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    academic_level VARCHAR(255) NOT NULL,
    enrollment_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS departement (
    departement_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(40) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS course (
    course_code INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) UNIQUE NOT NULL,
    credits INT NOT NULL CHECK (credits > 0),
    departement_id INT NOT NULL,
    FOREIGN KEY (departement_id) REFERENCES departement(departement_id)
);

CREATE TABLE IF NOT EXISTS semester (
    semester_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS instructor (
    instructor_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    departement_id INT NOT NULL,
    FOREIGN KEY (departement_id) REFERENCES departement(departement_id)
);

CREATE TABLE IF NOT EXISTS prerequisite (
    course_code INT NOT NULL,
    prereq_code INT NOT NULL,
    min_grade VARCHAR(20) NOT NULL,
    PRIMARY KEY (course_code, prereq_code),
    FOREIGN KEY (course_code) REFERENCES course(course_code),
    FOREIGN KEY (prereq_code) REFERENCES course(course_code)
);

CREATE TABLE IF NOT EXISTS course_result (
    result_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    course_code INT NOT NULL,
    grade VARCHAR(255) NOT NULL,
    status VARCHAR(10) NOT NULL CHECK (status IN ('PASS', 'NV')),
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (course_code) REFERENCES course(course_code)
);

CREATE TABLE IF NOT EXISTS section (
    section_id INT PRIMARY KEY AUTO_INCREMENT,
    course_code INT NOT NULL,
    semester_id INT NOT NULL,
    instructor_id INT NOT NULL,
    max_capacity INT NOT NULL,
    current_enrolled INT NOT NULL,
    day_of_week VARCHAR(30) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    room_location VARCHAR(40) NOT NULL,
    FOREIGN KEY (course_code) REFERENCES course(course_code),
    FOREIGN KEY (semester_id) REFERENCES semester(semester_id),
    FOREIGN KEY (instructor_id) REFERENCES instructor(instructor_id)
);

CREATE TABLE IF NOT EXISTS registration (
    registration_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    section_id INT NOT NULL,
    registration_date DATE NOT NULL,
    status VARCHAR(30) NOT NULL,
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (section_id) REFERENCES section(section_id)
);
CREATE OR REPLACE TRIGGER trg_check_prerequisite
BEFORE INSERT ON registration
FOR EACH ROW
DECLARE
    v_count NUMBER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM prerequisite p
    JOIN course_result cr
        ON cr.course_code = p.prereq_code
    JOIN grading_scale gs_student
        ON gs_student.grade_label = cr.grade
    JOIN grading_scale gs_min
        ON gs_min.grade_label = p.min_grade
    JOIN section s
        ON s.section_id = :NEW.section_id
    WHERE cr.student_id = :NEW.student_id
      AND s.course_code = p.course_code
      AND cr.status = 'PASS'
      AND gs_student.grade_rank >= gs_min.grade_rank;

    IF v_count = 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Prerequisite not satisfied');
    END IF;
END;
CREATE OR REPLACE TRIGGER trg_check_capacity
BEFORE INSERT ON registration
FOR EACH ROW
DECLARE
    v_current INT;
    v_max INT;
BEGIN
    SELECT current_enrolled, max_capacity
    INTO v_current, v_max
    FROM section
    WHERE section_id = :NEW.section_id;

    IF v_current >= v_max THEN
        RAISE_APPLICATION_ERROR(-20002, 'Section is full');
    END IF;
END;
CREATE OR REPLACE TRIGGER trg_no_duplicate_course
BEFORE INSERT ON registration
FOR EACH ROW
DECLARE
    v_count INT;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM registration r
    JOIN section s1 ON r.section_id = s1.section_id
    JOIN section s2 ON s2.section_id = :NEW.section_id
    WHERE r.student_id = :NEW.student_id
      AND s1.course_code = s2.course_code
      AND s1.semester_id = s2.semester_id;

    IF v_count > 0 THEN
        RAISE_APPLICATION_ERROR(-20003, 'Student already registered in this course');
    END IF;
END;
CREATE OR REPLACE TRIGGER trg_inc_enrolled
AFTER INSERT ON registration
FOR EACH ROW
BEGIN
    UPDATE section
    SET current_enrolled = current_enrolled + 1
    WHERE section_id = :NEW.section_id;
END;
CREATE OR REPLACE TRIGGER trg_dec_enrolled
AFTER DELETE ON registration
FOR EACH ROW
BEGIN
    UPDATE section
    SET current_enrolled = current_enrolled - 1
    WHERE section_id = :OLD.section_id;
END;
CREATE OR REPLACE TRIGGER trg_check_time
BEFORE INSERT OR UPDATE ON section
FOR EACH ROW
BEGIN
    IF :NEW.start_time >= :NEW.end_time THEN
        RAISE_APPLICATION_ERROR(-20004, 'Invalid time range');
    END IF;
END;
CREATE OR REPLACE TRIGGER trg_instructor_conflict
BEFORE INSERT OR UPDATE ON section
FOR EACH ROW
DECLARE
    v_count INT;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM section
    WHERE instructor_id = :NEW.instructor_id
      AND day_of_week = :NEW.day_of_week
      AND section_id <> NVL(:NEW.section_id, -1)
      AND (
            :NEW.start_time BETWEEN start_time AND end_time
         OR :NEW.end_time BETWEEN start_time AND end_time
      );

    IF v_count > 0 THEN
        RAISE_APPLICATION_ERROR(-20005, 'Instructor time conflict');
    END IF;
END;
CREATE OR REPLACE TRIGGER trg_room_conflict
BEFORE INSERT OR UPDATE ON section
FOR EACH ROW
DECLARE
    v_count INT;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM section
    WHERE room_location = :NEW.room_location
      AND day_of_week = :NEW.day_of_week
      AND section_id <> NVL(:NEW.section_id, -1)
      AND (
            :NEW.start_time BETWEEN start_time AND end_time
         OR :NEW.end_time BETWEEN start_time AND end_time
      );

    IF v_count > 0 THEN
        RAISE_APPLICATION_ERROR(-20006, 'Room already occupied');
    END IF;
END;
CREATE OR REPLACE TRIGGER trg_check_prerequisite_simple
BEFORE INSERT ON registration
FOR EACH ROW
DECLARE
    v_count INT;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM prerequisite p
    JOIN course_result cr ON cr.course_code = p.prereq_code
    JOIN section s ON s.course_code = p.course_code
    WHERE s.section_id = :NEW.section_id
      AND cr.student_id = :NEW.student_id
      AND cr.status = 'PASS';

    IF v_count = 0 THEN
        RAISE_APPLICATION_ERROR(-20007, 'Prerequisite not satisfied');
    END IF;
END;
CREATE OR REPLACE VIEW v_section_capacity AS
SELECT
    s.section_id,
    c.title AS course_title,
    s.max_capacity,
    s.current_enrolled,
    (s.max_capacity - s.current_enrolled) AS available_seats
FROM section s
JOIN course c ON s.course_code = c.course_code;
CREATE OR REPLACE VIEW v_registration_details AS
SELECT
    r.registration_id,
    st.student_id,
    st.first_name,
    st.last_name,
    c.title AS course_title,
    sem.name AS semester,
    r.registration_date,
    r.status
FROM registration r
JOIN student st ON r.student_id = st.student_id
JOIN section s ON r.section_id = s.section_id
JOIN course c ON s.course_code = c.course_code
JOIN semester sem ON s.semester_id = sem.semester_id;
CREATE OR REPLACE VIEW v_students_per_course AS
SELECT
    c.course_code,
    c.title AS course_title,
    COUNT(r.registration_id) AS total_students
FROM course c
JOIN section s ON c.course_code = s.course_code
LEFT JOIN registration r ON s.section_id = r.section_id
GROUP BY c.course_code, c.title;
CREATE OR REPLACE VIEW v_prerequisite_status AS
SELECT
    st.student_id,
    st.first_name,
    st.last_name,
    p.course_code AS target_course,
    p.prereq_code AS required_course,
    cr.status
FROM prerequisite p
JOIN course_result cr ON cr.course_code = p.prereq_code
JOIN student st ON st.student_id = cr.student_id;
CREATE OR REPLACE VIEW v_capacity_issues AS
SELECT
    section_id,
    max_capacity,
    current_enrolled
FROM section
WHERE current_enrolled > max_capacity;
CREATE OR REPLACE VIEW v_student_performance AS
SELECT
    st.student_id,
    st.first_name,
    st.last_name,
    c.title AS course_title,
    cr.grade,
    cr.status
FROM course_result cr
JOIN student st ON cr.student_id = st.student_id
JOIN course c ON cr.course_code = c.course_code;



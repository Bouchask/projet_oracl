/* SEED DATA ROBUSTE */
INSERT INTO departement (name) VALUES ('Informatique');
INSERT INTO departement (name) VALUES ('Mathematiques');

INSERT INTO semester (name, start_date, end_date) VALUES ('S1', TO_DATE('2025-09-01','YYYY-MM-DD'), TO_DATE('2026-01-30','YYYY-MM-DD'));
INSERT INTO semester (name, start_date, end_date) VALUES ('S2', TO_DATE('2026-02-01','YYYY-MM-DD'), TO_DATE('2026-06-30','YYYY-MM-DD'));
INSERT INTO semester (name, start_date, end_date) VALUES ('S3', TO_DATE('2026-09-01','YYYY-MM-DD'), TO_DATE('2027-01-30','YYYY-MM-DD'));

INSERT INTO salle (code_salle, capacity, building) VALUES ('A1', 50, 'Batiment A');
INSERT INTO salle (code_salle, capacity, building) VALUES ('B2', 30, 'Batiment B');
INSERT INTO salle (code_salle, capacity, building) VALUES ('Labo1', 20, 'Centre Info');

INSERT INTO filiere (name, departement_id) VALUES ('SMI', (SELECT departement_id FROM departement WHERE name = 'Informatique'));
INSERT INTO filiere (name, departement_id) VALUES ('SMA', (SELECT departement_id FROM departement WHERE name = 'Mathematiques'));

INSERT INTO app_user (code_apoge, password_hash, role) VALUES ('admin', '123', 'ADMIN');

INSERT INTO app_user (code_apoge, password_hash, role) VALUES ('PRF001', 'pass', 'TEACHER');
INSERT INTO instructor (code_apoge, name, email, departement_id) VALUES ('PRF001', 'Dr. Alami', 'alami@univ.ma', (SELECT departement_id FROM departement WHERE name = 'Informatique'));

INSERT INTO app_user (code_apoge, password_hash, role) VALUES ('STD001', 'pass', 'STUDENT');
INSERT INTO student (code_apoge, first_name, last_name, email, filiere_id, current_semester_id) VALUES ('STD001', 'Ahmed', 'Kamal', 'ahmed@etud.ma', (SELECT filiere_id FROM filiere WHERE name = 'SMI'), (SELECT semester_id FROM semester WHERE name = 'S3'));

INSERT INTO course (title, credits, total_hours, filiere_id, semester_id) VALUES ('Java Avance', 4, 40, (SELECT filiere_id FROM filiere WHERE name = 'SMI'), (SELECT semester_id FROM semester WHERE name = 'S3'));
INSERT INTO course (title, credits, total_hours, filiere_id, semester_id) VALUES ('Algo 1', 4, 40, (SELECT filiere_id FROM filiere WHERE name = 'SMI'), (SELECT semester_id FROM semester WHERE name = 'S1'));

INSERT INTO section (course_code, instructor_id, salle_id, max_capacity, day_of_week, start_time, end_time)
VALUES ((SELECT course_code FROM course WHERE title = 'Java Avance'), (SELECT instructor_id FROM instructor WHERE name = 'Dr. Alami'), (SELECT salle_id FROM salle WHERE code_salle = 'Labo1'), 20, 'Lundi', TO_DATE('2026-01-01 10:00','YYYY-MM-DD HH24:MI'), TO_DATE('2026-01-01 12:00','YYYY-MM-DD HH24:MI'));

COMMIT;
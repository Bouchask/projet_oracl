# 🎓 Advanced Course Registration System (Oracle DB)

![Oracle](https://img.shields.io/badge/Oracle-21c_XE-red?logo=oracle)
![Docker](https://img.shields.io/badge/Docker-Container-blue?logo=docker)
![Status](https://img.shields.io/badge/Status-Completed-success)

> **Project ID:** 19  
> **Module:** Administration Oracle  
> **Program:** Master SIIA (Systèmes d'Information et Intelligence Artificielle)  
> **Institution:** FPK (Faculté Polydisciplinaire Khouribga)

---

## 📋 Table of Contents
1. [Project Overview](#-project-overview)
2. [Database Architecture](#-database-architecture)
3. [Security & Access Control (RBAC)](#-security--access-control-rbac)
4. [Business Logic (Triggers)](#-business-logic-triggers)
5. [Analytics & Monitoring (Views)](#-analytics--monitoring-views)
6. [Setup & Installation](#-setup--installation)
7. [Connection Details](#-connection-details)
8. [Author](#-author)

---

## 🚀 Project Overview

This project implements a robust **Academic Course Registration System** using **Oracle Database 21c**. It is designed to handle complex university operations including student enrollment, course management, section scheduling, and grade processing.

**Key Features:**
* **Data Integrity:** Strict enforcement of foreign keys and check constraints.
* **Automation:** PL/SQL Triggers handle business logic (e.g., capacity checks, time conflicts).
* **Security:** Implements a **Role-Based Access Control (RBAC)** system with specific permissions for Admins, Teachers, and Students.
* **Analytics:** Pre-built Views for real-time reporting.

---

## 🏗 Database Architecture

The project is built on the **YAHYA_ADMIN** schema using a relational model. The schema ensures normalization and efficient data retrieval.

### Schema Diagram
The following Entity-Relationship diagram illustrates the connections between `STUDENT`, `COURSE`, `SECTION`, `REGISTRATION`, and other core tables.

![Schema Overview](images/Screenshot%20from%202026-01-15%2015-02-43.png)
*Figure 1: Global Database Schema and Relations.*

---

## 🔐 Security & Access Control (RBAC)

The system enforces the **Principle of Least Privilege** using Oracle Roles. Users are assigned only the permissions necessary for their function.

### 1. Defined Roles
| Role Name | Description | Key Permissions |
| :--- | :--- | :--- |
| **ROLE_ADMIN** | Full control over structural data. | `INSERT/UPDATE/DELETE` on Courses, Sections, Semesters. |
| **ROLE_TEACHER** | Academic management. | `INSERT/UPDATE` on Course Results (Grades). View Students. |
| **ROLE_STUDENT** | Enrollment access. | `INSERT` on Registration. View Courses & Sections. |

### 2. Functional Users
The following users were created to test the security model:

* **User:** `admin_user` → **Assigned Role:** `ROLE_ADMIN`
* **User:** `teacher_user` → **Assigned Role:** `ROLE_TEACHER`
* **User:** `student_user` → **Assigned Role:** `ROLE_STUDENT`

---

## ⚡ Business Logic (Triggers)

To ensure data consistency and enforce business rules, **PL/SQL Triggers** are used extensively. These triggers execute automatically during `INSERT`, `UPDATE`, or `DELETE` operations.

### Active Triggers
The system currently has the following triggers enabled:

![Triggers List](images/Screenshot%20from%202026-01-15%2015-10-40.png)
*Figure 2: List of active triggers in the system.*

### Detailed Trigger Implementation:

#### 1. Capacity Enforcement (`TRG_CHECK_CAPACITY`)
**Logic:** Before a student registers, the system checks if `current_enrolled` < `max_capacity`. If full, it raises an error.
![Trigger Capacity](images/Screenshot%20from%202026-01-15%2015-10-14.png)

#### 2. Duplicate Prevention (`TRG_NO_DUPLICATE_COURSE`)
**Logic:** Ensures a student cannot register for the same course twice in the same semester.
![Trigger Duplicate](images/Screenshot%20from%202026-01-15%2015-09-23.png)

#### 3. Enrollment Counters (`TRG_INC_ENROLLED`)
**Logic:** Automatically increments the student count in a section when a registration is added.
![Trigger Increment](images/Screenshot%20from%202026-01-15%2015-09-38.png)

#### 4. Time Validation (`TRG_CHECK_TIME`)
**Logic:** Validates that the section `start_time` is strictly earlier than `end_time`.
![Trigger Time Check](images/Screenshot%20from%202026-01-15%2015-09-06.png)

---

## 📊 Analytics & Monitoring (Views)

The system includes several **SQL Views** to simplify complex queries for administrators and teachers.

![Views List](images/Screenshot%20from%202026-01-15%2015-03-59.png)
*Figure 3: List of available Views.*

### Key Views Description:

| View Name | Description |
| :--- | :--- |
| **V_SECTION_CAPACITY** | Monitors seat availability and calculates `AVAILABLE_SEATS` dynamically. |
| **V_REGISTRATION_DETAILS** | Combines Student, Course, and Semester data for full reports. |
| **V_STUDENT_PERFORMANCE** | Aggregates grades and status (PASS/NV) for academic reporting. |
| **V_CAPACITY_ISSUES** | Alerts administrators to sections that are overbooked. |

### Visual Preview of Views:

**Registration Details (`V_REGISTRATION_DETAILS`):**
![Registration View](images/Screenshot%20from%202026-01-15%2015-06-04.png)

**Section Capacity (`V_SECTION_CAPACITY`):**
![Section Capacity View](images/Screenshot%20from%202026-01-15%2015-05-46.png)

**Student Performance (`V_STUDENT_PERFORMANCE`):**
![Performance View](images/Screenshot%20from%202026-01-15%2015-05-06.png)

---

## 🛠 Setup & Installation

### Prerequisites
* Docker Desktop
* DBeaver or SQL Developer
* Oracle Database 21c XE Image

### Installation Steps

1.  **Start Oracle Container:**
    ```bash
    docker exec -it oracle-db /bin/bash
    ```

2.  **Connect as SYSDBA:**
    ```sql
    sqlplus / as sysdba
    ```

3.  **Initialize Schema (One-time setup):**
    ```sql
    CREATE USER yahya_admin IDENTIFIED BY 123;
    GRANT DBA TO yahya_admin;
    ```

4.  **Run Deployment Scripts:**
    Connect as `yahya_admin` and execute the main SQL script followed by the security script.
    ```sql
    CONN yahya_admin/123
    @db.sql
    @security.sql
    ```

---

## 🔌 Connection Details

To connect via **DBeaver** or any external client, use the following configuration:

* **Host:** `localhost`
* **Port:** `1521`
* **Database (SID):** `XE` (or `ORCL` depending on setup)
* **Username:** `yahya_admin`
* **Role:** Normal

---

## 👨‍💻 Author

**Yahya Bouchak** *Master SIIA Student* *Faculté Polydisciplinaire Khouribga (FPK)*

> "Proudly developed in Morocco 🇲🇦."
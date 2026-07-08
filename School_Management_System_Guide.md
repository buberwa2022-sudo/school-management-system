# School Management System - Excel Format Guide
## NECTA Performance & Division Calculator

This guide will help you create a comprehensive School Management System in Excel that calculates student performance and assigns NECTA divisions.

---

## 📋 System Overview

The system includes the following components:

1. **Dashboard** - Summary statistics and overview
2. **Student Records** - Student information database
3. **Subject Marks** - Grade entry sheet
4. **Performance Analysis** - Automatic calculations
5. **Division Assignment** - NECTA grade divisions
6. **Reports** - Class statistics and rankings

---

## 🏗️ Sheet Structure

### Sheet 1: Dashboard
**Purpose:** Overview of school performance

| Field | Formula/Value |
|-------|---------------|
| School Name | [Enter School Name] |
| Class | [Enter Class] |
| Term | [Enter Term] |
| Academic Year | [Enter Year] |
| Total Students | =COUNTA(Students!A2:A101) |
| Average Performance | =AVERAGE(Performance!F2:F101) |
| Division I Count | =COUNTIF(Performance!H2:H101,"Division I") |
| Division II Count | =COUNTIF(Performance!H2:H101,"Division II") |
| Division III Count | =COUNTIF(Performance!H2:H101,"Division III") |
| Division IV Count | =COUNTIF(Performance!H2:H101,"Division IV") |

---

### Sheet 2: Students
**Purpose:** Student information database

| Column | Header | Data Type | Example |
|--------|--------|-----------|---------|
| A | Student ID | Text | STU001 |
| B | Full Name | Text | John Doe |
| C | Gender | Text | Male/Female |
| D | Date of Birth | Date | 01/01/2010 |
| E | Phone Number | Text | +255-XXX-XXXX |
| F | Parent Contact | Text | +255-XXX-XXXX |
| G | Admission Date | Date | 09/01/2023 |
| H | Status | Text | Active/Inactive |

**Notes:**
- Add new students starting from row 2
- Use consistent ID format (STU001, STU002, etc.)
- Status: Use "Active" for current students

---

### Sheet 3: Subjects
**Purpose:** Define all subjects for the class

| Column | Header | Example |
|--------|--------|---------|
| A | Subject Code | MATH |
| B | Subject Name | Mathematics |
| C | Subject Type | Core/Elective |
| D | Passing Mark | 40 |
| E | Maximum Marks | 100 |
| F | Weight | 1 |

**Standard NECTA Subjects (Example for Form 4):**
- Mathematics (MATH)
- English Language (ENG)
- Kiswahili Language (KIS)
- Physics (PHY)
- Chemistry (CHM)
- Biology (BIO)
- Geography (GEO)
- History (HIS)
- Civics (CIV)

---

### Sheet 4: Marks Entry
**Purpose:** Enter student marks for all subjects

**Structure:**
```
| A | B | C | D | E | F | G | H | I |
| Student ID | Student Name | MATH | ENG | KIS | PHY | CHM | BIO | GEO |
| STU001 | John Doe | 75 | 68 | 72 | 80 | 85 | 78 | 70 |
| STU002 | Jane Smith | 88 | 92 | 85 | 90 | 87 | 91 | 89 |
```

**Column Headers:**
- Column A: Student ID (Link from Students sheet)
- Column B: Student Name (Link from Students sheet)
- Column C onwards: Subject codes with marks (0-100)

---

### Sheet 5: Performance Analysis
**Purpose:** Automatic calculation of performance metrics

**Columns:**

| A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|
| Student ID | Name | Total Marks | Average | Grade | Points | Performance % | Division |
| =Marks!A2 | =Marks!B2 | =SUM(Marks!C2:I2) | =ROUND(C2/7,2) | [Grade Formula] | [Points] | =ROUND(C2/700*100,2) | [Division] |

**Formulas:**

#### Total Marks (Column C):
```
=SUM(Marks!C2:I2)
```

#### Average (Column D):
```
=ROUND(D2/7,2)
```

#### Grade Assignment (Column E):
```
=IF(D2>=80,"A",IF(D2>=70,"B",IF(D2>=60,"C",IF(D2>=50,"D",IF(D2>=40,"E","F")))))
```

#### Performance Points (Column F):
```
=IF(E2="A",5,IF(E2="B",4,IF(E2="C",3,IF(E2="D",2,IF(E2="E",1,0)))))
```

#### Performance Percentage (Column G):
```
=ROUND(C2/700*100,2)
```

#### Division Assignment (Column H) - **NECTA System**:
```
=IF(AVERAGE(Performance!C2:I2)>=70,"Division I",
   IF(AVERAGE(Performance!C2:I2)>=60,"Division II",
      IF(AVERAGE(Performance!C2:I2)>=50,"Division III",
         IF(AVERAGE(Performance!C2:I2)>=40,"Division IV","Failed"))))
```

---

## 📊 NECTA Division System

### Division Criteria:

| Division | Average Mark Range | Grade | Description |
|----------|-------------------|-------|-------------|
| Division I | 80-100 | A | Distinction |
| Division II | 70-79 | B/C | Credit |
| Division III | 60-69 | C/D | Pass |
| Division IV | 40-59 | D/E | Ordinary Pass |
| Failed | 0-39 | F | Below Pass |

---

## 📈 Sheet 6: Reports & Rankings

### Class Performance Summary

```
Total Students: =COUNTA(Performance!A2:A101)
Average Class Mark: =AVERAGE(Performance!C2:C101)
Highest Mark: =MAX(Performance!C2:C101)
Lowest Mark: =MIN(Performance!C2:C101)
Pass Rate: =ROUND(COUNTIF(Performance!H2:H101,"<>Failed")/COUNTA(Performance!A2:A101)*100,2)&"%"

Division Breakdown:
Division I: =COUNTIF(Performance!H2:H101,"Division I")
Division II: =COUNTIF(Performance!H2:H101,"Division II")
Division III: =COUNTIF(Performance!H2:H101,"Division III")
Division IV: =COUNTIF(Performance!H2:H101,"Division IV")
Failed: =COUNTIF(Performance!H2:H101,"Failed")
```

### Subject Performance Analysis

```
| Subject | Average Mark | Highest | Lowest | Pass Rate |
|---------|--------------|---------|--------|-----------|
| MATH | =AVERAGE(Marks!C2:C101) | =MAX(Marks!C2:C101) | =MIN(Marks!C2:C101) | [Formula] |
| ENG | =AVERAGE(Marks!D2:D101) | =MAX(Marks!D2:D101) | =MIN(Marks!D2:D101) | [Formula] |
```

### Top Performers

Use Data > Sort & Filter to rank students by total marks in descending order.

---

## 🔧 How to Use

### Step 1: Setup
1. Create a new Excel workbook
2. Create sheets with the names listed above
3. Add headers and formatting

### Step 2: Enter Data
1. In **Students sheet**: Add all student information
2. In **Subjects sheet**: List all subjects
3. In **Marks Entry**: Enter student marks

### Step 3: Auto-Calculate
All formulas in **Performance Analysis** sheet will automatically:
- Calculate totals and averages
- Assign grades
- Calculate performance points
- Assign NECTA divisions

### Step 4: Generate Reports
Use the **Reports** sheet to view:
- Class statistics
- Division breakdown
- Subject performance
- Student rankings

---

## 📝 Example Data

### Sample Student Data:
```
STU001 | John Doe | Male | 01/01/2008 | +255-712-123456 | +255-652-234567
STU002 | Jane Smith | Female | 05/03/2008 | +255-713-123457 | +255-653-234568
STU003 | Peter Johnson | Male | 12/07/2007 | +255-714-123458 | +255-654-234569
```

### Sample Marks:
```
STU001 | John Doe | 75 | 68 | 72 | 80 | 85 | 78 | 70
STU002 | Jane Smith | 88 | 92 | 85 | 90 | 87 | 91 | 89
STU003 | Peter Johnson | 52 | 45 | 48 | 55 | 58 | 50 | 47
```

---

## 🎨 Formatting Tips

### Color-Code Divisions:
- **Division I**: Green (#00B050)
- **Division II**: Blue (#0070C0)
- **Division III**: Yellow (#FFC000)
- **Division IV**: Orange (#FF6600)
- **Failed**: Red (#FF0000)

### Format Performance Percentage:
- Use conditional formatting to highlight:
  - 80-100: Green
  - 60-79: Yellow
  - 40-59: Orange
  - 0-39: Red

---

## 🔐 Data Validation

### For Marks Entry:
- Set data validation: Whole Number, between 0 and 100
- Apply to all marks columns

### For Gender:
- Set data validation: List → Male, Female

### For Status:
- Set data validation: List → Active, Inactive

---

## 💾 Backup & Maintenance

- Save the file regularly
- Keep a backup copy
- Use file versioning (e.g., SMS_Term1_2024.xlsx)
- Protect formulas with sheet protection

---

## 📞 Support Notes

- All formulas use standard Excel functions
- Compatible with Excel 2010 and later
- Can be used in Google Sheets with minor adjustments
- Works offline without internet

---

## Next Steps

1. Create the Excel file following this structure
2. Enter your school information
3. Add student data
4. Enter subject marks
5. Review auto-calculated performance and divisions
6. Generate reports for analysis


from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from mysql.connector import connect, Error
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from authtoken import verify_token, create_access_token
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from typing import List, Optional
from gpt import AiReport
import json

# 환경 변수 로드
load_dotenv()

# FastAPI 앱 인스턴스 생성
app = FastAPI()

# 비밀번호 해시 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# MySQL 연결 설정
def get_db_connection():
    try:
        connection = connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
        )
        return connection
    except Error as e:
        print(e)
        raise HTTPException(status_code=500, detail="DB 연결 실패")

# 모델 정의
class UserRegister(BaseModel):
    user_id: str
    password: str
    user_name: str


class UserLogin(BaseModel):
    user_id: str
    password: str


class ProfileSetRequest(BaseModel):
    user_id: str
    profile_name: str
    icon_url: str


class ProfileRemoveRequest(BaseModel):
    user_id: str
    profile_name: str

# 학습 시작 API 입력 모델
class StartLearningRequest(BaseModel):
    scenario_id: int
    user_id: str
    profile_name: str

# 학습 기록 API 입력 모델
class StepDataRequest(BaseModel):
    learning_log_id: int
    sceneId: str
    question: str
    answer: str
    response: str

# 반환 모델 정의
class LearningLogResponse(BaseModel):
    learning_log_id: int
    scenario_title: str
    scenario_pages: int
    num_of_answer_records: int
    learning_time: str

# 응답 모델 정의
class AnswerRecord(BaseModel):
    answer: str
    question: str
    response: str
    time: datetime
    scene: str

class CharacterUpdateRequest(BaseModel):
    user_id: str
    profile_name: str
    toggle: Optional[float] = 0.0
    prop: Optional[float] = 0.0
    eyeShape: Optional[float] = 0.0
    bodyShape: Optional[float] = 0.0
    bodyColor: Optional[float] = 0.0

class CharacterResponse(BaseModel):
    user_id: str
    profile_name: str
    toggle: Optional[float] = 0.0
    prop: Optional[float] = 0.0
    eyeShape: Optional[float] = 0.0
    bodyShape: Optional[float] = 0.0
    bodyColor: Optional[float] = 0.0

class AddLearningListRequest(BaseModel):
    user_id: str
    profile_name: str
    title: str

class ScenarioRequest(BaseModel):
    user_id: str
    profile_name: str

class RemoveLearningListRequest(BaseModel):
    user_id: str
    profile_name: str
    title: str

class AIReportRequest(BaseModel):
    learning_log_id: int

# 비밀번호 해싱
def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# 회원가입 엔드포인트
@app.post("/register")
async def register(user: UserRegister):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_pw = hash_password(user.password)

    query = "INSERT INTO users (user_id, password, user_name) VALUES (%s, %s, %s)"
    try:
        cursor.execute(query, (user.user_id, hashed_pw, user.user_name))
        conn.commit()
    except Error as e:
        raise HTTPException(status_code=400, detail="User already exists")
    finally:
        cursor.close()
        conn.close()

    return {"message": "User registered successfully"}


# 로그인 엔드포인트
@app.post("/login")
async def login(user: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT password, user_name FROM users WHERE user_id = %s"

    cursor.execute(query, (user.user_id,))
    result = cursor.fetchone()

    if not result or not verify_password(user.password, result[0]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 유효한 사용자일 경우 JWT 토큰 생성
    access_token = create_access_token(data={"sub": user.user_id})
    return {"user_name": result[1], "access_token": access_token, "token_type": "bearer"}


# 프로필 조회 엔드포인트
@app.get("/profiles/get/")
async def get_profiles(user_id: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT profile_name, icon_url FROM profiles WHERE user_id = %s"

    cursor.execute(query, (user_id,))
    profiles = cursor.fetchall()

    cursor.close()
    conn.close()

    if not profiles:
        raise HTTPException(status_code=404, detail="No profiles found for this user")

    return {"profiles": profiles}


# 프로필 설정/생성 엔드포인트
@app.post("/profiles/set/")
async def set_profile(profile_data: ProfileSetRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    query_check = "SELECT * FROM profiles WHERE user_id = %s AND profile_name = %s"
    cursor.execute(query_check, (profile_data.user_id, profile_data.profile_name))
    existing_profile = cursor.fetchone()

    if existing_profile:
        # 프로필이 존재하면 업데이트
        query_update = "UPDATE profiles SET icon_url = %s WHERE user_id = %s AND profile_name = %s"
        cursor.execute(query_update, (profile_data.icon_url, profile_data.user_id, profile_data.profile_name))
    else:
        # 프로필이 없으면 새로 생성
        query_insert = "INSERT INTO profiles (user_id, profile_name, icon_url) VALUES (%s, %s, %s)"
        cursor.execute(query_insert, (profile_data.user_id, profile_data.profile_name, profile_data.icon_url))

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Profile set successfully"}


# 프로필 삭제 엔드포인트
@app.delete("/profiles/rm/")
async def remove_profile(profile_data: ProfileRemoveRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "DELETE FROM profiles WHERE user_id = %s AND profile_name = %s"
    cursor.execute(query, (profile_data.user_id, profile_data.profile_name))

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Profile not found")

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Profile removed successfully"}

# 학습 시작 API
@app.post("/learn/start")
async def start_learning(request: StartLearningRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO learning_logs (scenario_id, user_id, profile_name, time)
        VALUES (%s, %s, %s, %s)
    """
    current_time = datetime.now()

    try:
        cursor.execute(query, (request.scenario_id, request.user_id, request.profile_name, current_time))
        conn.commit()
        learning_log_id = cursor.lastrowid
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to create learning log record: {e}")
    finally:
        cursor.close()
        conn.close()

    return {"learning_log_id": learning_log_id}

# 학습 기록 API
@app.post("/learn/step")
async def log_step_data(request: StepDataRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO answers (learning_log_id, sceneId, question, answer, response)
        VALUES (%s, %s, %s, %s, %s)
    """

    try:
        cursor.execute(query, (request.learning_log_id, request.sceneId, request.question, request.answer, request.response))
        conn.commit()
    except Error as e:
        raise HTTPException(status_code=500, detail="Failed to log step data")
    finally:
        cursor.close()
        conn.close()

    return {"message": "Step data recorded successfully"}

# 학습 기록 조회 API
@app.get("/learn/logs", response_model=List[LearningLogResponse])
async def get_learning_logs(user_id: str, profile_name: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            l.learning_log_id AS learning_log_id,
            s.title AS scenario_title, 
            l.time AS learning_time, 
            s.scene_cnt AS scenario_pages, 
            COUNT(a.learning_log_id) AS num_of_answer_records
        FROM 
            edu_for_disabled.learning_logs l
        JOIN 
            edu_for_disabled.scenario s ON l.scenario_id = s.scenario_id
        LEFT JOIN 
            edu_for_disabled.answers a ON l.learning_log_id = a.learning_log_id
        WHERE 
            l.user_id = %s AND l.profile_name = %s
        GROUP BY 
            l.learning_log_id, s.title, l.time, s.scene_cnt
        ORDER BY
            l.time DESC
    """
    try:
        cursor.execute(query, (user_id, profile_name))
        logs = cursor.fetchall()

        if not logs:
            return []

        # Convert `learning_time` to string in ISO format
        for log in logs:
            log['learning_time'] = log['learning_time'].isoformat()

        return logs
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve learning logs: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.get("/answers", response_model=List[AnswerRecord])
async def get_answers(learning_log_id: int = Query(...)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            answer, 
            question,
            response, 
            time, 
            sceneId AS scene 
        FROM answers 
        WHERE learning_log_id = %s
    """

    try:
        cursor.execute(query, (learning_log_id,))
        results = cursor.fetchall()

        if not results:
            raise HTTPException(status_code=404, detail="No records found for the given learning_log_id")

        return results
    except Error as e:
        print(f"Error fetching records: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch records")
    finally:
        cursor.close()
        conn.close()

# 캐릭터 커스텀 생성 또는 갱신 API
@app.post("/character/update")
async def update_character(request: CharacterUpdateRequest):
    query_insert_or_update = """
    INSERT INTO edu_for_disabled.character (user_id, profile_name, toggle, prop, eyeShape, bodyShape, bodyColor)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        toggle = VALUES(toggle),
        prop = VALUES(prop),
        eyeShape = VALUES(eyeShape),
        bodyShape = VALUES(bodyShape),
        bodyColor = VALUES(bodyColor)
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            query_insert_or_update,
            (
                request.user_id,
                request.profile_name,
                request.toggle,
                request.prop,
                request.eyeShape,
                request.bodyShape,
                request.bodyColor,
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    return {"message": "Character updated successfully"}

# 캐릭터 커스텀 조회 API
@app.get("/character/get", response_model=CharacterResponse)
async def get_character(user_id: str, profile_name: str):
    query_select = """
    SELECT user_id, profile_name, toggle, prop, eyeShape, bodyShape, bodyColor
    FROM edu_for_disabled.character
    WHERE user_id = %s AND profile_name = %s
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query_select, (user_id, profile_name))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            raise HTTPException(status_code=404, detail="Character not found")

        return result
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.post("/learning_list/add")
async def add_learning_list_entry(request: AddLearningListRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # scenario_id를 title로 조회
        query_scenario = """
            SELECT scenario_id
            FROM edu_for_disabled.scenario
            WHERE title = %s
        """
        cursor.execute(query_scenario, (request.title,))
        scenario = cursor.fetchone()

        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario with given title not found")

        scenario_id = scenario[0]

        # learning_list에 레코드 추가
        query_insert = """
            INSERT INTO edu_for_disabled.learning_list (user_id, profile_name, scenario_id)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query_insert, (request.user_id, request.profile_name, scenario_id))
        conn.commit()

    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()

    return {"message": "Learning list entry added successfully"}

@app.post("/learning_list/scenarios")
async def get_scenarios_by_user_and_profile(request: ScenarioRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 시나리오 title 조회 쿼리
        query = """
            SELECT s.title
            FROM edu_for_disabled.learning_list l
            JOIN edu_for_disabled.scenario s ON l.scenario_id = s.scenario_id
            WHERE l.user_id = %s AND l.profile_name = %s
        """
        cursor.execute(query, (request.user_id, request.profile_name))
        results = cursor.fetchall()

        # 데이터가 없는 경우 빈 리스트 반환
        if not results:
            return {"titles": []}

        # 결과를 title 목록으로 반환
        titles = [row[0] for row in results]

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()

    return {"titles": titles}

@app.post("/learning_list/remove")
async def remove_learning_list_entry(request: RemoveLearningListRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 시나리오 ID를 가져오기 위한 쿼리
        query_get_scenario_id = """
            SELECT scenario_id
            FROM edu_for_disabled.scenario
            WHERE title = %s
        """
        cursor.execute(query_get_scenario_id, (request.title,))
        scenario = cursor.fetchone()

        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario title not found")

        scenario_id = scenario[0]

        # learning_list 레코드 삭제 쿼리
        query_delete = """
            DELETE FROM edu_for_disabled.learning_list
            WHERE user_id = %s AND profile_name = %s AND scenario_id = %s
        """
        cursor.execute(query_delete, (request.user_id, request.profile_name, scenario_id))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="No matching learning list record found")

    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()

    return {"message": "Learning list entry removed successfully"}


@app.post("/learn/ai_report")
async def generate_ai_report(request: AIReportRequest):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Step 1: Verify and fetch `learning_log_id` and associated `scenario_id`
        query = """
            SELECT scenario_id 
            FROM edu_for_disabled.learning_logs 
            WHERE learning_log_id = %s
        """
        cursor.execute(query, (request.learning_log_id,))
        learning_log = cursor.fetchone()

        if not learning_log:
            raise HTTPException(status_code=404, detail="Learning log not found")

        scenario_id = learning_log["scenario_id"]

        # Step 2: Fetch `scenario` data
        query = """
            SELECT * 
            FROM edu_for_disabled.scenario 
            WHERE scenario_id = %s
        """
        cursor.execute(query, (scenario_id,))
        scenario_data = cursor.fetchall()

        if not scenario_data:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # Step 3: Fetch `answers` data
        query = """
            SELECT * 
            FROM edu_for_disabled.answers 
            WHERE learning_log_id = %s
        """
        cursor.execute(query, (request.learning_log_id,))
        answers_data = cursor.fetchall()

        # Step 4: Generate AI report
        result = json.loads(AiReport(scenario_data, answers_data))

        # Step 5: Insert result into `learning_report` table
        query = """
            INSERT INTO edu_for_disabled.learning_report (
                learning_log_id, completed, agile, accuracy, context, pronunciation, review
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                request.learning_log_id,
                result["completed"],
                result["agile"],
                result["accuracy"],
                result["context"],
                result["pronunciation"],
                result["review"],
            ),
        )
        # Step 6: Update or Insert into `edu_for_disabled.statics`
        statics_query = """
                    INSERT INTO edu_for_disabled.statics (
                        learning_log_id, correct_response_cnt, timeout_response_cnt
                    ) VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        correct_response_cnt = VALUES(correct_response_cnt),
                        timeout_response_cnt = VALUES(timeout_response_cnt),
                        updated_at = CURRENT_TIMESTAMP
                """
        cursor.execute(
            statics_query,
            (
                request.learning_log_id,
                result["correct_response_cnt"],
                result["timeout_response_cnt"],
            ),
        )

        conn.commit()

        return {"message": "AI report generated successfully", "report": result}

    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

    finally:
        cursor.close()
        conn.close()

@app.get("/learn/ai_report")
async def get_ai_report(learning_log_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch the AI report for the given learning_log_id
        query = """
            SELECT * 
            FROM edu_for_disabled.learning_report 
            WHERE learning_log_id = %s
        """
        cursor.execute(query, (learning_log_id,))
        report = cursor.fetchone()

        if not report:
            raise HTTPException(status_code=404, detail="AI report not found for the given learning_log_id")

        return report

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

    finally:
        cursor.close()
        conn.close()

@app.get("/statics")
async def get_statistics(user_id: str, profile_name: str, start_date: str = None, end_date: str = None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Build query conditionally based on date parameters
        query = """
                    SELECT learning_log_id, scenario_id
                    FROM edu_for_disabled.learning_logs
                    WHERE user_id = %s AND profile_name = %s
                """
        params = [user_id, profile_name]

        if start_date and end_date:
            query += " AND time BETWEEN %s AND %s"
            params.extend([start_date, end_date])

        cursor.execute(query, tuple(params))
        learning_logs = cursor.fetchall()

        if not learning_logs:
            raise HTTPException(status_code=404, detail="No learning logs found for the given criteria")

        learning_log_ids = [log["learning_log_id"] for log in learning_logs]
        if not learning_log_ids:
            # If no matching logs, return zero counts
            return {
                "whole_response_cnt": 0,
                "responsed_question_cnt": 0,
                "expected_question_cnt": 0,
                "eval_response_cnt": 0,
                "correct_response_cnt": 0,
                "timeout_response_cnt": 0
            }

        # Calculate whole_response_cnt(전체 응답수)
        query = """
               SELECT COUNT(*) as whole_response_cnt
               FROM edu_for_disabled.answers
               WHERE learning_log_id IN (%s)
           """ % ",".join(["%s"] * len(learning_log_ids))
        cursor.execute(query, learning_log_ids)
        whole_response_cnt = cursor.fetchall()[0]["whole_response_cnt"]

        # Calculate real_response_cnt(응답한 문항수)
        query = """
            SELECT COUNT(*) as responsed_question_cnt
            FROM (
                SELECT MAX(hash_num) as latest_hash_num
                FROM edu_for_disabled.answers
                WHERE learning_log_id IN (%s)
                GROUP BY learning_log_id, sceneId
            ) as latest_answers
        """ % ",".join(["%s"] * len(learning_log_ids))

        cursor.execute(query, learning_log_ids)
        responsed_question_cnt = cursor.fetchall()[0]["responsed_question_cnt"]

        # Calculate expect_response_cnt(전체 문항수)
        query = """
            SELECT SUM(s.scene_cnt) as expected_question_cnt
            FROM edu_for_disabled.scenario s
            JOIN edu_for_disabled.learning_logs l ON s.scenario_id = l.scenario_id
            WHERE l.learning_log_id IN (%s)
        """ % ",".join(["%s"] * len(learning_log_ids))
        cursor.execute(query, learning_log_ids)
        expected_question_cnt = cursor.fetchall()[0]["expected_question_cnt"] or 0

        query = """
            SELECT COUNT(*) AS answer_count
            FROM edu_for_disabled.answers a
            WHERE a.learning_log_id IN (
                SELECT lr.learning_log_id
                FROM edu_for_disabled.learning_report lr
                WHERE lr.learning_log_id IN (%s)
            )
        """ % ",".join(["%s"] * len(learning_log_ids))

        # 쿼리 실행
        cursor.execute(query, learning_log_ids)
        eval_response_cnt = cursor.fetchone()["answer_count"] or 0

        # Calculate correct_response_cnt
        query = """
            SELECT SUM(correct_response_cnt) as correct_response_cnt
            FROM edu_for_disabled.statics
            WHERE learning_log_id IN (%s)
        """ % ",".join(["%s"] * len(learning_log_ids))
        cursor.execute(query, learning_log_ids)
        correct_response_cnt = cursor.fetchall()[0]["correct_response_cnt"] or 0

        # Calculate timeout_response_cnt
        query = """
            SELECT SUM(timeout_response_cnt) as timeout_response_cnt
            FROM edu_for_disabled.statics
            WHERE learning_log_id IN (%s)
        """ % ",".join(["%s"] * len(learning_log_ids))
        cursor.execute(query, learning_log_ids)
        timeout_response_cnt = cursor.fetchall()[0]["timeout_response_cnt"] or 0

        # Return the results as a JSON response
        return {
            "whole_response_cnt": whole_response_cnt,
            "responsed_question_cnt": responsed_question_cnt,
            "expected_question_cnt": expected_question_cnt,
            "eval_response_cnt": eval_response_cnt,
            "correct_response_cnt": correct_response_cnt,
            "timeout_response_cnt": timeout_response_cnt
        }

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        cursor.close()
        conn.close()
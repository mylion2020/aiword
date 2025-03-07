from datetime import datetime
from flask import render_template, request, jsonify
from wxcloudrun import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import pymysql
import os
import hashlib
import re


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    print('you are in index')
    return render_template('index.html')
    #return 'hello'


@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)


def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='111111',
        database='ai-word',
        charset='utf8',  # 修改为与数据库一致的字符集
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/api/book-list', methods=['GET'])
def get_book_list():
    """
    获取book表的所有数据
    :return: JSON格式的图书列表
    """
    try:
        # 建立数据库连接
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 根据book表结构执行查询
            sql = """
                SELECT book_id, book_name, stage 
                FROM book 
                ORDER BY book_id
            """
            cursor.execute(sql)
            books = cursor.fetchall()
            
        # 关闭连接
        conn.close()
        
        # 返回结果
        return jsonify({
            'code': 0,
            'data': books,
            'message': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'code': -1,
            'data': [],
            'message': f'查询失败：{str(e)}'
        })

@app.route('/api/user/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        password = data.get('password')
        nickname = data.get('nickname')
        openid = data.get('openid')

        # 参数验证
        if not all([phone, password]):
            return make_err_response('手机号和密码不能为空')
        
        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return make_err_response('手机号格式不正确')

        # 密码加密
        password_hash = hashlib.md5(password.encode()).hexdigest()

        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 检查手机号是否已注册
            cursor.execute('SELECT user_id FROM user WHERE phone = %s', (phone,))
            if cursor.fetchone():
                return make_err_response('该手机号已注册')

            # 插入新用户
            sql = """
                INSERT INTO user (phone, password, nickname, openid, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (phone, password_hash, nickname, openid, datetime.now()))
            conn.commit()

            # 获取新用户信息
            cursor.execute('SELECT user_id, phone, nickname FROM user WHERE phone = %s', (phone,))
            user = cursor.fetchone()

        return make_succ_response(user)

    except Exception as e:
        return make_err_response(f'注册失败：{str(e)}')
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/user/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        password = data.get('password')
        openid = data.get('openid')

        if not phone or not (password or openid):
            return make_err_response('参数不完整')

        conn = get_db_connection()
        with conn.cursor() as cursor:
            if password:
                # 密码登录
                # password_hash = hashlib.md5(password.encode()).hexdigest()
                password_hash=password
                sql = 'SELECT user_id, phone, nickname FROM user WHERE phone = %s AND password = %s'
                cursor.execute(sql, (phone, password_hash))
            else:
                # openid登录
                sql = 'SELECT user_id, phone, nickname FROM user WHERE phone = %s AND openid = %s'
                cursor.execute(sql, (phone, openid))

            user = cursor.fetchone()
            if not user:
                return make_err_response('用户名或密码错误')

            # 更新最后登录时间
            cursor.execute('UPDATE user SET last_login = %s WHERE user_id = %s', 
                         (datetime.now(), user['user_id']))
            conn.commit()

        return make_succ_response(user)

    except Exception as e:
        return make_err_response(f'登录失败：{str(e)}')
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/plan/books', methods=['GET'])
def get_books():
    """获取可选择的词书列表"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
                SELECT b.book_id, b.book_name, b.stage,
                       COUNT(bw.word) as word_count
                FROM book b
                LEFT JOIN book_word bw ON b.book_id = bw.book_id
                GROUP BY b.book_id, b.book_name, b.stage
                ORDER BY b.stage, b.book_id
            """
            cursor.execute(sql)
            books = cursor.fetchall()
            
        return make_succ_response(books)
    except Exception as e:
        return make_err_response(f'获取词书列表失败：{str(e)}')
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/plan/set', methods=['POST'])
def set_plan():
    """设置学习计划"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        book_id = data.get('book_id')
        new_word = data.get('new_word')
        review = data.get('review')

        if not all([user_id, book_id, new_word, review]):
            return make_err_response('参数不完整')

        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 检查是否已有计划
            cursor.execute('SELECT * FROM plan WHERE user_id = %s', (user_id,))
            existing_plan = cursor.fetchone()

            if existing_plan:
                # 更新现有计划
                sql = """
                    UPDATE plan 
                    SET book_id = %s, new_word = %s, review = %s
                    WHERE user_id = %s
                """
                cursor.execute(sql, (book_id, new_word, review, user_id))
            else:
                # 创建新计划
                sql = """
                    INSERT INTO plan (user_id, book_id, new_word, review)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (user_id, book_id, new_word, review))
            
            conn.commit()

        return make_succ_response({
            'user_id': user_id,
            'book_id': book_id,
            'new_word': new_word,
            'review': review
        })
    except Exception as e:
        return make_err_response(f'设置计划失败：{str(e)}')
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/plan/get', methods=['GET'])
def get_plan():
    """获取用户的学习计划"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return make_err_response('缺少用户ID')

        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
                SELECT p.*, b.book_name, b.stage
                FROM plan p
                JOIN book b ON p.book_id = b.book_id
                WHERE p.user_id = %s
            """
            cursor.execute(sql, (user_id,))
            plan = cursor.fetchone()

        return make_succ_response(plan if plan else {})
    except Exception as e:
        return make_err_response(f'获取计划失败：{str(e)}')
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/progress/today', methods=['GET'])
def get_today_progress():
    """获取今日学习进度"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return make_err_response('缺少用户ID')

        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 获取今日新学单词数
            sql = """
                SELECT COUNT(*) as count
                FROM user_word
                WHERE user_id = %s 
                AND learn_date = CURDATE()
                AND status = 1
            """
            cursor.execute(sql, (user_id,))
            new_learned = cursor.fetchone()['count']

            # 获取今日复习单词数
            sql = """
                SELECT COUNT(*) as count
                FROM user_word
                WHERE user_id = %s 
                AND review_date = CURDATE()
                AND status = 2
            """
            cursor.execute(sql, (user_id,))
            reviewed = cursor.fetchone()['count']

        return make_succ_response({
            'newLearned': new_learned,
            'reviewed': reviewed
        })
    except Exception as e:
        return make_err_response(f'获取进度失败：{str(e)}')
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取学习统计"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return make_err_response('缺少用户ID')

        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 获取已学单词总数
            sql = """
                SELECT COUNT(*) as count
                FROM user_word
                WHERE user_id = %s
            """
            cursor.execute(sql, (user_id,))
            total_learned = cursor.fetchone()['count']

            # 获取已掌握单词数
            sql = """
                SELECT COUNT(*) as count
                FROM user_word
                WHERE user_id = %s AND status = 3
            """
            cursor.execute(sql, (user_id,))
            mastered = cursor.fetchone()['count']

            # 获取连续打卡天数
            sql = """
                SELECT COUNT(DISTINCT date) as streak
                FROM log
                WHERE user_id = %s
                AND date >= (
                    SELECT MAX(date) - INTERVAL 
                    (SELECT COUNT(*) - 1 FROM (
                        SELECT DISTINCT date 
                        FROM log 
                        WHERE user_id = %s
                        ORDER BY date DESC
                    ) t) DAY
                    FROM log 
                    WHERE user_id = %s
                )
            """
            cursor.execute(sql, (user_id, user_id, user_id))
            streak = cursor.fetchone()['streak']

        return make_succ_response({
            'totalLearned': total_learned,
            'mastered': mastered,
            'streak': streak
        })
    except Exception as e:
        return make_err_response(f'获取统计失败：{str(e)}')
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/word/new', methods=['GET'])
def get_new_words():
    """获取新单词列表"""
    try:
        user_id = request.args.get('user_id')
        count = request.args.get('count', type=int)
        
        if not all([user_id, count]):
            return make_err_response('参数不完整')

        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 获取用户的词书ID
            cursor.execute('SELECT book_id FROM plan WHERE user_id = %s', (user_id,))
            plan = cursor.fetchone()
            if not plan:
                return make_err_response('未设置学习计划')

            # 获取未学习的单词
            sql = """
                SELECT w.word, w.phonetic, w.translation, w.definition, w.audio
                FROM book_word bw
                JOIN word_list w ON bw.word = w.word
                WHERE bw.book_id = %s
                AND bw.word NOT IN (
                    SELECT word FROM user_word WHERE user_id = %s
                )
                LIMIT %s
            """
            cursor.execute(sql, (plan['book_id'], user_id, count))
            words = cursor.fetchall()

        return make_succ_response(words)
    except Exception as e:
        return make_err_response(f'获取单词失败：{str(e)}')
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/word/learn', methods=['POST'])
def save_learned_word():
    """保存学习记录"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        word = data.get('word')
        status = data.get('status', 1)  # 1: 新学习
        
        if not all([user_id, word]):
            return make_err_response('参数不完整')

        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 插入学习记录
            sql = """
                INSERT INTO user_word (
                    user_id, word, status, learn_date, 
                    rem_rank, review_count, error_count
                )
                VALUES (%s, %s, %s, CURDATE(), 0, 0, 0)
            """
            cursor.execute(sql, (user_id, word, status))
            conn.commit()

        return make_succ_empty_response()
    except Exception as e:
        return make_err_response(f'保存记录失败：{str(e)}')
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/word/review', methods=['GET'])
def get_review_words():
    """获取待复习单词列表"""
    try:
        user_id = request.args.get('user_id')
        count = request.args.get('count', type=int)
        
        if not all([user_id, count]):
            return make_err_response('参数不完整')

        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 获取需要复习的单词
            # 按照记忆等级和上次复习时间排序
            sql = """
                SELECT w.word, w.phonetic, w.translation, w.definition, w.audio,
                       uw.rem_rank, uw.review_count, uw.error_count
                FROM user_word uw
                JOIN word_list w ON uw.word = w.word
                WHERE uw.user_id = %s
                AND uw.status < 3  -- 未完全掌握的单词
                AND (
                    uw.review_date IS NULL  -- 从未复习过
                    OR DATE(uw.review_date) < CURDATE()  -- 今天还未复习
                )
                ORDER BY uw.rem_rank ASC, uw.review_date ASC
                LIMIT %s
            """
            cursor.execute(sql, (user_id, count))
            words = cursor.fetchall()

        return make_succ_response(words)
    except Exception as e:
        return make_err_response(f'获取复习单词失败：{str(e)}')
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/word/review', methods=['POST'])
def update_review_status():
    """更新单词复习状态"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        word = data.get('word')
        is_correct = data.get('is_correct', True)
        
        if not all([user_id, word]):
            return make_err_response('参数不完整')

        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 获取当前单词状态
            cursor.execute("""
                SELECT rem_rank, review_count, error_count, status
                FROM user_word
                WHERE user_id = %s AND word = %s
            """, (user_id, word))
            current = cursor.fetchone()
            
            if not current:
                return make_err_response('单词记录不存在')

            # 更新记忆等级和复习次数
            new_rank = current['rem_rank']
            new_status = current['status']
            
            if is_correct:
                new_rank = min(5, current['rem_rank'] + 1)  # 最高5级
                if new_rank >= 5 and current['review_count'] >= 5:
                    new_status = 3  # 完全掌握
            else:
                new_rank = max(0, current['rem_rank'] - 1)  # 最低0级
                
            # 更新记录
            sql = """
                UPDATE user_word
                SET rem_rank = %s,
                    status = %s,
                    review_date = CURDATE(),
                    review_count = review_count + 1,
                    error_count = error_count + %s
                WHERE user_id = %s AND word = %s
            """
            cursor.execute(sql, (
                new_rank,
                new_status,
                0 if is_correct else 1,
                user_id,
                word
            ))
            conn.commit()

        return make_succ_empty_response()
    except Exception as e:
        return make_err_response(f'更新复习状态失败：{str(e)}')
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """获取用户详细信息"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return make_err_response('缺少用户ID')

        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 获取用户基本信息
            sql = """
                SELECT user_id, phone, nickname, created_at, last_login
                FROM user
                WHERE user_id = %s
            """
            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return make_err_response('用户不存在')

            # 获取学习数据统计
            sql = """
                SELECT 
                    COUNT(*) as total_words,
                    SUM(CASE WHEN status = 3 THEN 1 ELSE 0 END) as mastered_words,
                    SUM(review_count) as total_reviews,
                    SUM(error_count) as total_errors
                FROM user_word
                WHERE user_id = %s
            """
            cursor.execute(sql, (user_id,))
            stats = cursor.fetchone()

            # 获取最近7天的学习记录
            sql = """
                SELECT 
                    DATE(learn_date) as date,
                    COUNT(*) as word_count
                FROM user_word
                WHERE user_id = %s
                AND learn_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                GROUP BY DATE(learn_date)
                ORDER BY date DESC
            """
            cursor.execute(sql, (user_id,))
            weekly_stats = cursor.fetchall()

            # 合并数据
            user['stats'] = stats
            user['weekly_stats'] = weekly_stats

        return make_succ_response(user)
    except Exception as e:
        return make_err_response(f'获取用户信息失败：{str(e)}')
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/user/update', methods=['POST'])
def update_user_profile():
    """更新用户信息"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        nickname = data.get('nickname')
        
        if not all([user_id, nickname]):
            return make_err_response('参数不完整')

        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
                UPDATE user
                SET nickname = %s
                WHERE user_id = %s
            """
            cursor.execute(sql, (nickname, user_id))
            conn.commit()

        return make_succ_empty_response()
    except Exception as e:
        return make_err_response(f'更新用户信息失败：{str(e)}')
    finally:
        if 'conn' in locals():
            conn.close()

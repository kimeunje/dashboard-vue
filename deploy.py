#!/usr/bin/env python3
# deploy.py - Vue 빌드 파일을 Flask 서버에 배포하는 스크립트

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(command, cwd=None):
    """명령어 실행 - 인코딩 문제 해결"""
    print(f"실행 중: {command}")
    try:
        # Windows 환경에서 인코딩 문제 해결
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=True,
            capture_output=True, 
            text=True,
            encoding='utf-8',  # UTF-8 인코딩 명시
            errors='ignore'    # 디코딩 에러 무시
        )
        if result.stdout:
            print(f"성공: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"오류 발생:")
        if e.stderr:
            try:
                print(f"stderr: {e.stderr}")
            except:
                print("stderr 출력 시 인코딩 오류 발생")
        if e.stdout:
            try:
                print(f"stdout: {e.stdout}")
            except:
                print("stdout 출력 시 인코딩 오류 발생")
        return False
    except Exception as e:
        print(f"예상치 못한 오류: {e}")
        return False


def run_command_alternative(command, cwd=None):
    """대안 명령어 실행 방법 - 실시간 출력"""
    print(f"실행 중: {command}")
    try:
        # 실시간 출력으로 인코딩 문제 우회
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='ignore',
            bufsize=1,
            universal_newlines=True
        )
        
        # 실시간으로 출력 읽기
        for line in process.stdout:
            print(line.rstrip())
        
        process.wait()
        
        if process.returncode == 0:
            print("✅ 명령어 실행 성공")
            return True
        else:
            print(f"❌ 명령어 실행 실패 (반환 코드: {process.returncode})")
            return False
            
    except Exception as e:
        print(f"예상치 못한 오류: {e}")
        return False


def deploy_vue_to_flask():
    """Vue 빌드 파일을 Flask 서버로 배포"""

    # 경로 설정
    current_dir = Path.cwd()
    vue_project_dir = current_dir / "front-end"  # Vue 프로젝트 경로
    flask_project_dir = current_dir / "back-end"  # Flask 프로젝트 경로

    vue_dist_dir = vue_project_dir / "dist"
    flask_static_dir = flask_project_dir / "static"

    print("=== Vue 프로젝트를 Flask 서버에 배포 ===")

    # 1. Vue 프로젝트 존재 확인
    if not vue_project_dir.exists():
        print(f"❌ Vue 프로젝트 디렉토리를 찾을 수 없습니다: {vue_project_dir}")
        return False

    # 2. Flask 프로젝트 존재 확인
    if not flask_project_dir.exists():
        print(f"❌ Flask 프로젝트 디렉토리를 찾을 수 없습니다: {flask_project_dir}")
        return False

    # 3. Vue 프로젝트 빌드 (대안 방법 사용)
    print("📦 Vue 프로젝트 빌드 중...")
    if not run_command_alternative("npm run build", cwd=vue_project_dir):
        print("❌ Vue 빌드 실패")
        return False

    # 4. 빌드 파일 존재 확인
    if not vue_dist_dir.exists():
        print(f"❌ 빌드 파일을 찾을 수 없습니다: {vue_dist_dir}")
        return False

    # 5. 기존 static 폴더 백업 (있다면)
    if flask_static_dir.exists():
        backup_dir = flask_static_dir.parent / "static_backup"
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        print(f"📂 기존 static 폴더 백업: {backup_dir}")
        shutil.move(str(flask_static_dir), str(backup_dir))

    # 6. Vue 빌드 파일을 Flask static 폴더로 복사
    print(f"📁 빌드 파일 복사: {vue_dist_dir} → {flask_static_dir}")
    shutil.copytree(str(vue_dist_dir), str(flask_static_dir))

    # 7. index.html을 templates 폴더에도 복사 (필요한 경우)
    flask_templates_dir = flask_project_dir / "templates"
    flask_templates_dir.mkdir(exist_ok=True)

    index_html_src = flask_static_dir / "index.html"
    index_html_dst = flask_templates_dir / "index.html"

    if index_html_src.exists():
        shutil.copy2(str(index_html_src), str(index_html_dst))
        print(f"📄 index.html 복사: {index_html_dst}")

    print("✅ 배포 완료!")
    print(f"   - 정적 파일: {flask_static_dir}")
    print(f"   - 템플릿 파일: {flask_templates_dir}")
    print("")
    print("🚀 Flask 서버 실행 방법:")
    print(f"   cd {flask_project_dir}")
    print("   python mock_app.py")

    return True


def clean_deployment():
    """배포된 파일들 정리"""
    current_dir = Path.cwd()
    flask_project_dir = current_dir / "back-end"
    flask_static_dir = flask_project_dir / "static"
    flask_templates_dir = flask_project_dir / "templates"
    backup_dir = flask_project_dir / "static_backup"

    print("🧹 배포 파일 정리 중...")

    if flask_static_dir.exists():
        shutil.rmtree(flask_static_dir)
        print(f"   - 삭제됨: {flask_static_dir}")

    if flask_templates_dir.exists():
        index_file = flask_templates_dir / "index.html"
        if index_file.exists():
            index_file.unlink()
            print(f"   - 삭제됨: {index_file}")

    # 백업 복원
    if backup_dir.exists():
        shutil.move(str(backup_dir), str(flask_static_dir))
        print(f"   - 백업 복원: {flask_static_dir}")

    print("✅ 정리 완료!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        clean_deployment()
    else:
        # 환경 변수 설정으로 인코딩 문제 완화
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        deploy_vue_to_flask()
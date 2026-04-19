"""
Vector Store 초기 설정 스크립트
- 용도: OpenAI Vector Store를 생성하고 목표/일기 문서를 업로드
- 실행: uv run python setup_vector_store.py [파일경로...]
- 인자 없이 실행하면 data/my_goals.md를 기본으로 업로드
- 결과: .env 파일에 VECTOR_STORE_ID가 기록됨
- 필수 환경변수: OPENAI_API_KEY
"""

import sys
import time
from pathlib import Path

from dotenv import load_dotenv, set_key
from openai import OpenAI

load_dotenv()

# 지원 파일 형식
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}

# 폴링 설정
POLL_INTERVAL_SEC = 2
POLL_TIMEOUT_SEC = 120


def create_vector_store(client: OpenAI, name: str = "Life Coach Knowledge Base") -> str:
    """Vector Store를 생성하고 ID를 반환한다."""
    vs = client.vector_stores.create(name=name)
    print(f"Vector Store 생성 완료: {vs.id} ({vs.name})")
    return vs.id


def upload_files(client: OpenAI, vector_store_id: str, file_paths: list[Path]) -> None:
    """파일들을 Vector Store에 업로드한다.
    upload_and_poll 대신 업로드 → 수동 폴링으로 타임아웃을 제어한다.
    """
    for path in file_paths:
        if not path.exists():
            print(f"  [SKIP] 파일 없음: {path}")
            continue
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            print(f"  [SKIP] 미지원 형식: {path.suffix} ({path.name})")
            continue

        try:
            # 1단계: OpenAI Files API에 파일 업로드
            print(f"  업로드 중: {path.name}...", end=" ", flush=True)
            with open(path, "rb") as f:
                file_obj = client.files.create(file=f, purpose="assistants")
            print(f"file_id={file_obj.id}", flush=True)

            # 2단계: Vector Store에 파일 연결
            print(f"  Vector Store에 연결 중...", end=" ", flush=True)
            vs_file = client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=file_obj.id,
            )

            # 3단계: 수동 폴링 (타임아웃 적용)
            elapsed = 0
            while vs_file.status in ("in_progress", "queued"):
                if elapsed >= POLL_TIMEOUT_SEC:
                    print(f"\n  [TIMEOUT] {POLL_TIMEOUT_SEC}초 초과. 백그라운드에서 처리 중일 수 있습니다.")
                    break
                time.sleep(POLL_INTERVAL_SEC)
                elapsed += POLL_INTERVAL_SEC
                print(".", end="", flush=True)
                vs_file = client.vector_stores.files.retrieve(
                    vector_store_id=vector_store_id,
                    file_id=file_obj.id,
                )

            if vs_file.status == "completed":
                print(f"\n  [OK] 완료: {path.name} (file_id: {file_obj.id})")
            elif vs_file.status == "failed":
                error_msg = getattr(vs_file, "last_error", "알 수 없는 오류")
                print(f"\n  [FAILED] 실패: {path.name} - {error_msg}")
            else:
                print(f"\n  [STATUS] {path.name}: {vs_file.status} (file_id: {file_obj.id})")

        except Exception as e:
            print(f"\n  [ERROR] 업로드 실패: {path.name} - {e}")


def save_vector_store_id(vector_store_id: str) -> None:
    """Vector Store ID를 .env 파일에 저장한다."""
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        # .env.example에서 복사
        example_path = Path(__file__).parent / ".env.example"
        if example_path.exists():
            env_path.write_text(example_path.read_text())
        else:
            env_path.write_text("")

    set_key(str(env_path), "VECTOR_STORE_ID", vector_store_id)
    print(f"\n.env 파일에 VECTOR_STORE_ID={vector_store_id} 저장 완료")


def main():
    client = OpenAI()

    # 파일 경로 결정: 인자가 있으면 인자 사용, 없으면 기본 파일
    if len(sys.argv) > 1:
        file_paths = [Path(p) for p in sys.argv[1:]]
    else:
        default_file = Path(__file__).parent / "data" / "my_goals.md"
        file_paths = [default_file]

    print("=== Life Coach Vector Store 초기 설정 ===\n")

    # 1. Vector Store 생성
    vs_id = create_vector_store(client)

    # 2. 파일 업로드
    print(f"\n파일 업로드 중 ({len(file_paths)}개)...")
    upload_files(client, vs_id, file_paths)

    # 3. .env에 ID 저장
    save_vector_store_id(vs_id)

    print("\n=== 설정 완료 ===")
    print("이제 'uv run streamlit run app.py'로 앱을 실행하세요.")


if __name__ == "__main__":
    main()

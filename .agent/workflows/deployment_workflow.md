---
description: daily-seongsu.bit-habit.com 배포 전체 구조 (k3s, Gradio, GitHub Actions CD)
---

# 배포 전체 구조

## 0. 전체 흐름 요약

```
[개발자] git push main
    │
    ▼
[GitHub Actions: CI] ── ci.yml ──▶ lint(ruff) + test(pytest)
    │ CI 성공 시
    ▼
[GitHub Actions: CD] ── deploy.yml ──▶ SSH → 서버에서 git pull + docker compose up
    │
    ▼
[서버: Docker Container] daily-seongsu-container
  └── python guidebook/gradio_app.py → 0.0.0.0:7860 에서 Gradio 실행
    │
    ▼
[K3s / Traefik Ingress] ── 443 (HTTPS) 수신
  └── daily-seongsu-svc (K8s Service: 80 → 7860)
       └── Endpoint → 호스트 IP 10.0.0.61:7860 (Docker 컨테이너)
    │
    ▼
[사용자 브라우저] https://daily-seongsu.bit-habit.com/
```

---

## 1. Gradio 앱 설정

### 실행 방식
- **실행 명령**: `python guidebook/gradio_app.py --demo-name daily_seongsu`
- **바인딩**: `0.0.0.0:7860` (환경변수 `GRADIO_SERVER_NAME`, `GRADIO_SERVER_PORT`)
- **컨테이너 이름**: `daily-seongsu-container`

### Dockerfile (2-stage build)
```
Stage 1 (builder): python:3.11-slim-bookworm
  └── requirements.txt 설치 → /install

Stage 2 (runtime): python:3.11-slim-bookworm
  └── /install 복사 (비root 사용자 appuser)
  └── EXPOSE 7860
  └── CMD ["python", "guidebook/gradio_app.py", "--demo-name", "daily_seongsu"]
```

### docker-compose.yml
| 항목 | 값 |
|---|---|
| image | `daily-seongsu:latest` |
| ports | `7860:7860` |
| restart | `unless-stopped` |
| healthcheck | `curl http://localhost:7860/` (30s 간격) |
| resource limit | CPU 1.0, Memory 1G |
| volumes | `data_features_level2.csv`, `train_data.csv`, `test_data.csv` |
| env_file | `.env` |

### 배포 위치
```
/home/ubuntu/workspace/daily_seongsu/
├── Dockerfile
├── docker-compose.yml
├── .env
└── guidebook/
    └── gradio_app.py   ← 진입점
```

---

## 2. K3s 설정

### 아키텍처
K3s는 **Traefik**을 내장 Ingress Controller로 사용한다.
```
인터넷 : 443
   │
   ▼
Traefik (K3s 내장) :443/:80
   │   TLS 종료 (tls-secret)
   ▼
Ingress Rules (04-ingress.yaml 또는 k8s/ingress.yaml)
   │
   ├── daily-seongsu.bit-habit.com → daily-seongsu-svc:80
   ├── blog.bit-habit.com          → blog-svc:80
   ├── wiki.bit-habit.com          → wiki-svc:80
   ├── booktoss.bit-habit.com      → booktoss-svc:80
   ├── bit-habit.com               → static-web-svc:80
   ├── habit.bit-habit.com /api/   → fastapi-svc:80
   ├── startpage.bit-habit.com     → fastapi-svc:80
   ├── viz.bit-habit.com           → viz-svc:80
   └── status.bit-habit.com        → static-web-svc:80
```

### K8s 매니페스트 파일 구조

```
k3s_migration/            ← 초기 마이그레이션 버전
├── 02-external-services.yaml   ← 호스트 앱 연결 (Service + Endpoints)
├── 03-static-deployment.yaml   ← 정적 파일 서빙 (Nginx Pod + ConfigMap)
└── 04-ingress.yaml             ← 도메인 라우팅 규칙

k8s/                      ← 현재 운영 버전 (cert-manager 적용)
├── ingress.yaml                ← 도메인 라우팅 (cert-manager 어노테이션 추가)
└── cert-manager/
    ├── aws-secret.yaml         ← AWS Route53 Access Key Secret
    ├── cluster-issuer.yaml     ← Let's Encrypt ACME 발급자 설정
    └── certificate.yaml        ← 인증서 요청 (bit-habit.com + *.bit-habit.com)
```

### daily-seongsu-svc 동작 원리
`daily-seongsu`는 K8s 클러스터 외부(호스트)에서 Docker로 실행되므로,
**Headless Service + Endpoints** 패턴으로 연결한다:

```yaml
# Service: 클러스터 내부 DNS 이름 제공 (daily-seongsu-svc:80)
kind: Service
  name: daily-seongsu-svc
  port: 80 → targetPort: 7860

# Endpoints: 실제 트래픽 목적지 (호스트 Docker 컨테이너)
kind: Endpoints
  name: daily-seongsu-svc
  ip: 10.0.0.61   ← 서버 호스트 IP
  port: 7860      ← Docker 컨테이너 포트
```

### TLS / HTTPS (cert-manager)
```
cert-manager (ClusterIssuer: letsencrypt-prod)
   └── ACME DNS-01 Challenge
        └── AWS Route53 API → _acme-challenge TXT 레코드 자동 생성
             └── Let's Encrypt 인증 → tls-secret 자동 갱신

Ingress → spec.tls.secretName: tls-secret 참조
```

| 리소스 | 파일 | 역할 |
|---|---|---|
| `ClusterIssuer` | `cluster-issuer.yaml` | Let's Encrypt ACME 발급자, Route53 DNS-01 사용 |
| `Certificate` | `certificate.yaml` | `bit-habit.com` + `*.bit-habit.com` 인증서 요청 |
| `Secret` (tls-secret) | cert-manager 자동 생성 | Traefik이 TLS 종료에 사용 |
| `Secret` (route53-credentials-secret) | `aws-secret.yaml` | AWS Route53 API 키 |

---

## 3. daily-seongsu.bit-habit.com 요청 흐름 (단계별)

```
① 사용자가 https://daily-seongsu.bit-habit.com/ 입력

② DNS 조회
   daily-seongsu.bit-habit.com → AWS Route53 → 서버 공인 IP

③ TCP 연결: 서버 :443

④ Traefik (K3s 내장)
   - TLS 종료: tls-secret (cert-manager가 자동 갱신한 Let's Encrypt 인증서)
   - SNI: daily-seongsu.bit-habit.com 확인

⑤ Ingress 라우팅 (k8s/ingress.yaml)
   - host: daily-seongsu.bit-habit.com
   - backend: daily-seongsu-svc:80

⑥ K8s Service (daily-seongsu-svc)
   - 포트 매핑: 80 → 7860

⑦ Endpoints
   - 목적지: 10.0.0.61:7860 (호스트 서버)

⑧ Docker Container (daily-seongsu-container)
   - 포트: 7860 (호스트) → 7860 (컨테이너)
   - Gradio 앱 응답 반환

⑨ 사용자 화면에 Gradio UI 표시
```

---

## 4. GitHub Actions CD 파이프라인

### 트리거 조건
```
CI 워크플로우("Daily Seongsu CI") 성공 후 자동 실행
   또는
workflow_dispatch (수동 실행)
```

### ci.yml (CI 워크플로우)
**트리거**: `push` 또는 `PR` → `main` 브랜치

| 단계 | 내용 |
|---|---|
| Checkout | 코드 체크아웃 |
| Python 3.10 설정 | pip 캐시 활성화 |
| 의존성 설치 | `requirements.txt` + `crawler/requirements.txt` |
| Lint (ruff) | `ruff check . --output-format=github` (오류 시 계속 진행) |
| Test (pytest) | `pytest tests/ -v --cov=. --cov-report=term-missing` |

### deploy.yml (CD 워크플로우)
**트리거**: CI 성공 후 자동 실행 (또는 수동)

```
GitHub Actions Runner (ubuntu-latest)
│
│ 1. SSH 키 설정
│    secrets.SSH_KEY_PIPE (|로 구분된 PEM) → 줄바꿈 복원 → ~/.ssh/deploy_key
│    ssh-keyscan → ~/.ssh/known_hosts
│
│ 2. SSH 접속
│    ssh -i deploy_key {SERVER_USER}@{SERVER_HOST}
│
▼ 서버에서 실행 (bash heredoc):
│
│ 3. git fetch origin main
│    git diff HEAD origin/main → 변경사항 파악
│    git reset --hard origin/main → 로컬을 remote와 강제 동기화
│
│ 4. 변경사항 있을 경우:
│    docker compose up -d --build  ← 이미지 재빌드 + 컨테이너 재시작
│    docker image prune -f          ← 오래된 이미지 정리
│
│ 5. 변경사항 없을 경우: 스킵
```

### GitHub Secrets 필요 항목
| Secret 이름 | 내용 |
|---|---|
| `SSH_KEY_PIPE` | RSA PEM 개인키 (`\n` → `\|` 로 인코딩) |
| `SERVER_HOST` | 서버 IP 또는 도메인 |
| `SERVER_USER` | SSH 사용자명 (예: `ubuntu`) |

---

## 5. 주요 운영 명령어

```bash
# K3s 상태 확인
kubectl get pods,svc,ingress,endpoints

# K3s 인증서 상태 확인
kubectl get certificate,clusterissuer

# Gradio 앱 수동 재시작
cd /home/ubuntu/workspace/daily_seongsu
docker compose restart

# K8s Ingress 규칙 재적용
kubectl apply -f /home/ubuntu/workspace/daily_seongsu/k8s/ingress.yaml

# K9s (터미널 대시보드)
k9s
```

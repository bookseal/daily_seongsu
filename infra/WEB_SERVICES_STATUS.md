# bit-habit.com 웹서비스 현황

> 작성일: 2026-03-12  
> 환경: Oracle Cloud ARM64, Ubuntu 20.04  
> 인프라: **k3s (실제 운영)** + Docker (일부 앱)  

---

## 전체 아키텍처 개요

```
외부 인터넷 (443/80)
       │
  iptables NAT
       │
  klipper-lb (svclb-traefik pod, hostPort 80/443)
       │
  Traefik (k3s 기본 Ingress Controller)
       │
  Kubernetes Ingress (main-ingress, default namespace)
       │
  각 Service → 실제 앱 (Pod 또는 호스트 프로세스)
```

- **TLS**: cert-manager + Let's Encrypt (`*.bit-habit.com` 와일드카드)
- **TLS Secret**: `tls-secret` (default namespace)
- **k8s context**: `default` (실제 운영 클러스터, k3s)
- **주의**: k3d 개발 클러스터(`k3d-dev-cluster`)는 별개로 존재함

---

## 서비스별 현황

### 1. bit-habit.com (메인 사이트)

| 항목 | 내용 |
|------|------|
| **URL** | https://bit-habit.com, https://www.bit-habit.com |
| **k8s Service** | `static-web-svc` (ClusterIP) |
| **k8s Pod** | `static-web` Deployment (nginx:alpine) |
| **실제 파일** | hostPath: `/var/www/html` |
| **운영 방식** | k8s Pod (nginx) |

**특이사항**: `/habit/` 경로도 동일 Pod에서 서빙 (hostPath: `/var/www/habit`)

---

### 2. habit.bit-habit.com (BitHabit Flutter 앱)

| 항목 | 내용 |
|------|------|
| **URL** | https://habit.bit-habit.com |
| **k8s Service (정적)** | `static-web-svc` (ClusterIP) |
| **k8s Service (API)** | `fastapi-svc` → `10.0.0.61:8000` ← **⚠️ 포트 충돌 (startpage와 동일)** |
| **정적 파일** | hostPath: `/home/ubuntu/workspace/bithabit_flutter/build/web` |
| **API 앱** | `bithabit-api.service` (systemd), uvicorn, FastAPI |
| **API 소스** | `/home/ubuntu/workspace/bithabit_api/` |
| **운영 방식** | 정적: k8s Pod (nginx) / API: systemd (host) |

**⚠️ 문제**: `fastapi-svc` endpoint가 `10.0.0.61:8000`인데, 이 포트를 `startpage.service`도 사용 중 → **포트 충돌**  
**해결 필요**: bithabit-api를 다른 포트(예: 8002)로 변경 + 별도 k8s Service 생성

---

### 3. startpage.bit-habit.com (시작 페이지)

| 항목 | 내용 |
|------|------|
| **URL** | https://startpage.bit-habit.com |
| **k8s Service** | `fastapi-svc` → `10.0.0.61:8000` |
| **앱** | `startpage.service` (systemd), uvicorn, FastAPI |
| **소스** | `/home/ubuntu/workspace/my-start-page/` |
| **포트** | 8000 |
| **운영 방식** | systemd (host) |

---

### 4. blog.bit-habit.com (Ghost 블로그)

| 항목 | 내용 |
|------|------|
| **URL** | https://blog.bit-habit.com |
| **k8s Service** | `blog-svc` → `10.0.0.61:2368` |
| **앱** | Ghost CMS (`ghost_158-180-71-122.service`, systemd) |
| **실행** | `/usr/bin/node /usr/bin/ghost run` |
| **포트** | 2368 |
| **DB** | MySQL (`mysql.service`) |
| **운영 방식** | systemd (host) |

---

### 5. booktoss.bit-habit.com (BookToss)

| 항목 | 내용 |
|------|------|
| **URL** | https://booktoss.bit-habit.com |
| **k8s Service** | `booktoss-svc` → `10.0.0.61:8501` |
| **앱** | `booktoss-streamlit.service` (systemd), Streamlit |
| **소스** | `/home/ubuntu/workspace/Booktoss/app.py` |
| **포트** | 8501 |
| **운영 방식** | systemd (host) |

---

### 6. daily-seongsu.bit-habit.com (일일 성수)

| 항목 | 내용 |
|------|------|
| **URL** | https://daily-seongsu.bit-habit.com |
| **k8s Service** | `daily-seongsu-svc` → `10.42.0.26:7860` |
| **앱** | `daily-seongsu` Deployment (k8s Pod) |
| **이미지** | `daily-seongsu:latest` (로컬 빌드) |
| **포트** | 7860 |
| **운영 방식** | k8s Pod |

---

### 7. wiki.bit-habit.com (Wiki.js)

| 항목 | 내용 |
|------|------|
| **URL** | https://wiki.bit-habit.com |
| **k8s Service** | `wiki-svc` → `10.0.0.61:3001` |
| **앱** | Docker Compose (`wikijs-wiki-1`) |
| **이미지** | `ghcr.io/requarks/wiki:2` |
| **포트** | 3001 (host) → 3000 (container) |
| **DB** | PostgreSQL (`wikijs-db-1` Docker 컨테이너) |
| **운영 방식** | Docker Compose |

---

### 8. code-server.bit-habit.com (VS Code Server)

| 항목 | 내용 |
|------|------|
| **URL** | https://code-server.bit-habit.com |
| **k8s Service** | `code-server-svc` → `10.0.0.61:8081` |
| **앱** | `code-server@ubuntu.service` (systemd) |
| **실행** | `/usr/bin/code-server` |
| **포트** | 8081 |
| **운영 방식** | systemd (host) |

---

### 9. seoul-apt.bit-habit.com (서울 아파트 가격)

| 항목 | 내용 |
|------|------|
| **URL** | https://seoul-apt.bit-habit.com |
| **k8s Service** | `seoul-apt-price` → `10.42.0.28:8501` |
| **앱** | `seoul-apt-price` Deployment (k8s Pod) |
| **이미지** | `seoul-apt-price:latest` (로컬 빌드) |
| **포트** | 8501 |
| **운영 방식** | k8s Pod |

---

### 10. viz.bit-habit.com (선형대수 시각화)

| 항목 | 내용 |
|------|------|
| **URL** | https://viz.bit-habit.com |
| **k8s Service** | `viz-svc` → `10.0.0.61:8503` |
| **앱** | `viz-platform` Docker 컨테이너 |
| **이미지** | `viz-bit-habit:latest` (로컬 빌드) |
| **포트** | 8503 (host) → 8501 (container) |
| **운영 방식** | Docker (단일 컨테이너) |

---

## 현재 구조 요약

```
호스트 프로세스 (systemd)        k8s Pod                    Docker 컨테이너
─────────────────────           ─────────────────────      ─────────────────────
startpage    :8000              static-web (nginx)         wikijs-wiki    :3001
bithabit-api :8000 ⚠️충돌       daily-seongsu  :7860       wikijs-db      :5432
ghost        :2368              seoul-apt-price:8501       viz-platform   :8503
booktoss     :8501              cert-manager
code-server  :8081
```

---

## 파악된 문제점

### ⚠️ 포트 충돌
- **`startpage.service`**: 포트 8000 사용
- **`bithabit-api.service`**: 포트 8000 사용 (새로 추가됨)
- **결과**: 두 서비스 중 하나만 작동하고 나머지는 bind 실패로 재시작 루프

### 개선 필요사항
- `bithabit-api`를 별도 포트(예: 8002)로 변경
- habit.bit-habit.com용 별도 k8s Service 추가 (`bithabit-api-svc: 8002`)
- k8s Ingress에서 habit.bit-habit.com `/api/` → `bithabit-api-svc`로 분리

---

## 관련 파일 위치

| 파일 | 경로 |
|------|------|
| k8s Ingress | `/home/ubuntu/workspace/daily_seongsu/infra/k8s-global/ingress.yaml` |
| nginx ConfigMap | `kubectl --context=default get configmap nginx-conf -n default` |
| BitHabit Flutter | `/home/ubuntu/workspace/bithabit_flutter/` |
| BitHabit API | `/home/ubuntu/workspace/bithabit_api/` |
| StartPage | `/home/ubuntu/workspace/my-start-page/` |
| Booktoss | `/home/ubuntu/workspace/Booktoss/` |
| Static HTML | `/var/www/html/` |
| Legacy Habit | `/var/www/habit/` |
| systemd 서비스 | `/etc/systemd/system/` |

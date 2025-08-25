{{/*
Expand the name of the chart.
*/}}
{{- define "oatie.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "oatie.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "oatie.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "oatie.labels" -}}
helm.sh/chart: {{ include "oatie.chart" . }}
{{ include "oatie.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "oatie.selectorLabels" -}}
app.kubernetes.io/name: {{ include "oatie.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Backend labels
*/}}
{{- define "oatie.backend.labels" -}}
{{ include "oatie.labels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "oatie.backend.selectorLabels" -}}
{{ include "oatie.selectorLabels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "oatie.frontend.labels" -}}
{{ include "oatie.labels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "oatie.frontend.selectorLabels" -}}
{{ include "oatie.selectorLabels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "oatie.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "oatie.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Generate image repository with registry
*/}}
{{- define "oatie.image.repository" -}}
{{- if .Values.global.imageRegistry }}
{{- printf "%s/%s" .Values.global.imageRegistry .repository }}
{{- else }}
{{- .repository }}
{{- end }}
{{- end }}

{{/*
Backend image
*/}}
{{- define "oatie.backend.image" -}}
{{- $registry := .Values.global.imageRegistry | default "" }}
{{- $repository := .Values.image.backend.repository }}
{{- $tag := .Values.image.backend.tag | default .Chart.AppVersion }}
{{- if $registry }}
{{- printf "%s/%s:%s" $registry $repository $tag }}
{{- else }}
{{- printf "%s:%s" $repository $tag }}
{{- end }}
{{- end }}

{{/*
Frontend image
*/}}
{{- define "oatie.frontend.image" -}}
{{- $registry := .Values.global.imageRegistry | default "" }}
{{- $repository := .Values.image.frontend.repository }}
{{- $tag := .Values.image.frontend.tag | default .Chart.AppVersion }}
{{- if $registry }}
{{- printf "%s/%s:%s" $registry $repository $tag }}
{{- else }}
{{- printf "%s:%s" $repository $tag }}
{{- end }}
{{- end }}

{{/*
Database URL
*/}}
{{- define "oatie.databaseUrl" -}}
{{- if .Values.secrets.values.databaseUrl }}
{{- .Values.secrets.values.databaseUrl }}
{{- else if .Values.postgresql.enabled }}
{{- $host := printf "%s-postgresql" (include "oatie.fullname" .) }}
{{- $port := .Values.postgresql.primary.service.ports.postgresql | default 5432 }}
{{- $database := .Values.postgresql.auth.database }}
{{- $username := .Values.postgresql.auth.username }}
{{- printf "postgresql+asyncpg://%s:$(POSTGRES_PASSWORD)@%s:%d/%s" $username $host $port $database }}
{{- else }}
{{- required "Database URL must be provided when PostgreSQL is disabled" .Values.secrets.values.databaseUrl }}
{{- end }}
{{- end }}

{{/*
Redis URL
*/}}
{{- define "oatie.redisUrl" -}}
{{- if .Values.secrets.values.redisUrl }}
{{- .Values.secrets.values.redisUrl }}
{{- else if .Values.redis.enabled }}
{{- $host := printf "%s-redis-master" (include "oatie.fullname" .) }}
{{- $port := .Values.redis.master.service.ports.redis | default 6379 }}
{{- if .Values.redis.auth.enabled }}
{{- printf "redis://:$(REDIS_PASSWORD)@%s:%d/0" $host $port }}
{{- else }}
{{- printf "redis://%s:%d/0" $host $port }}
{{- end }}
{{- else }}
{{- required "Redis URL must be provided when Redis is disabled" .Values.secrets.values.redisUrl }}
{{- end }}
{{- end }}

{{/*
Environment-specific values
*/}}
{{- define "oatie.environmentValues" -}}
{{- $env := .Values.environment | default "production" }}
{{- if hasKey .Values.environments $env }}
{{- .Values.environments | index $env | toYaml }}
{{- end }}
{{- end }}

{{/*
Blue-Green deployment suffix
*/}}
{{- define "oatie.blueGreenSuffix" -}}
{{- if eq .Values.deploymentStrategy.type "blue-green" }}
{{- if .Values.deploymentStrategy.blueGreen.productionSlot }}
{{- printf "-%s" .Values.deploymentStrategy.blueGreen.productionSlot }}
{{- else }}
{{- "-blue" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Canary deployment suffix
*/}}
{{- define "oatie.canarySuffix" -}}
{{- if eq .Values.deploymentStrategy.type "canary" }}
{{- "-canary" }}
{{- end }}
{{- end }}

{{/*
Generate secret key if not provided
*/}}
{{- define "oatie.secretKey" -}}
{{- if .Values.config.app.secretKey }}
{{- .Values.config.app.secretKey }}
{{- else }}
{{- randAlphaNum 64 }}
{{- end }}
{{- end }}

{{/*
Generate encryption key if not provided
*/}}
{{- define "oatie.encryptionKey" -}}
{{- if .Values.config.app.encryptionKey }}
{{- .Values.config.app.encryptionKey }}
{{- else }}
{{- randAlphaNum 32 }}
{{- end }}
{{- end }}

{{/*
Common annotations
*/}}
{{- define "oatie.annotations" -}}
{{- if .Values.deploymentStrategy.type }}
deployment.kubernetes.io/strategy: {{ .Values.deploymentStrategy.type }}
{{- end }}
{{- if eq .Values.deploymentStrategy.type "blue-green" }}
deployment.kubernetes.io/slot: {{ .Values.deploymentStrategy.blueGreen.productionSlot | default "blue" }}
{{- end }}
{{- end }}

{{/*
Pod annotations
*/}}
{{- define "oatie.podAnnotations" -}}
prometheus.io/scrape: "true"
prometheus.io/port: "8000"
prometheus.io/path: "/metrics"
checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
checksum/secret: {{ include (print $.Template.BasePath "/secret.yaml") . | sha256sum }}
{{- end }}
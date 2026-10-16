{{- define "stockpilot.fullname" -}}
{{- .Release.Name | trunc 50 | trimSuffix "-" -}}
{{- end -}}

{{- define "stockpilot.labels" -}}
app.kubernetes.io/part-of: stockpilot
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/instance: {{ .Release.Name }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{- define "stockpilot.backendSelector" -}}
app: {{ include "stockpilot.fullname" . }}-backend
{{- end -}}

{{- define "stockpilot.frontendSelector" -}}
app: {{ include "stockpilot.fullname" . }}-frontend
{{- end -}}

{{- define "stockpilot.postgresSelector" -}}
app: {{ include "stockpilot.fullname" . }}-postgres
{{- end -}}

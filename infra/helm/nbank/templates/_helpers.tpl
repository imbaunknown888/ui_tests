{{- define "nbank.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- define "nbank.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "nbank.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
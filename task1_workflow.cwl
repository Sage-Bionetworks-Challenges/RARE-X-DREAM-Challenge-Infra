#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow
label: RARE-X A Rare Disease Open Science Data Challenge Evaluation Task 1
doc: >
  This workflow will run and validate project submissions to the
  RARE-X Challenge (syn51198355). These submissions will manually
  by reviewed and scored by a team of judges.

requirements:
  - class: StepInputExpressionRequirement

inputs:
  submissionId:
    label: Submission ID
    type: int
  submitterUploadSynId:
    label: Synapse Folder ID accessible by the submitter
    type: string
  synapseConfig:
    label: filepath to .synapseConfig file
    type: File
  admin:
    label: Synapse team that will should have access to writeup
    type: string
    default: "RARE-X Organizers"

outputs: {}

steps:

  validate:
    doc: Validate submission, which is expected to be a Synapse Project
    run: writeup-workflow/validate.cwl
    in:
      - id: synapse_config
        source: "#synapseConfig"
      - id: submissionid
        source: "#submissionId"
      - id: challengewiki
        valueFrom: "syn51198355"
      - id: admin
        source: "#admin"
    out:
      - id: results
      - id: status
      - id: invalid_reasons
  
  email_validation:
    doc: Send validation results to submitter
    run: steps/task1_email.cwl
    in:
      - id: submissionid
        source: "#submissionId"
      - id: synapse_config
        source: "#synapseConfig"
      - id: status
        source: "#validate/status"
      - id: invalid_reasons
        source: "#validate/invalid_reasons"
    out: [finished]

  annotate_validation_with_output:
    doc: Add `submission_status` and `submission_errors` annotations to submission
    run: |-
      https://raw.githubusercontent.com/Sage-Bionetworks/ChallengeWorkflowTemplates/v3.1/cwl/annotate_submission.cwl
    in:
      - id: submissionid
        source: "#submissionId"
      - id: annotation_values
        source: "#validate/results"
      - id: to_public
        default: true
      - id: force
        default: true
      - id: synapse_config
        source: "#synapseConfig"
    out: [finished]

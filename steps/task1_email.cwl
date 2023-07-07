#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool

requirements:
- class: InlineJavascriptRequirement
- class: InitialWorkDirRequirement
  listing:
  - entryname: send_email.py
    entry: |
      #!/usr/bin/env python
      import synapseclient
      import argparse
      import json

      parser = argparse.ArgumentParser()
      parser.add_argument("-s", "--submissionid", required=True, help="Submission ID")
      parser.add_argument("-c", "--synapse_config", required=True, help="credentials file")
      parser.add_argument("--status", required=True, help="Prediction File Status")
      parser.add_argument("-i", "--invalid", help="Invalid reasons")

      args = parser.parse_args()
      syn = synapseclient.Synapse(configPath=args.synapse_config)
      syn.login(silent=True)

      sub = syn.getSubmission(args.submissionid)
      participantid = sub.get("teamId")
      if participantid is not None:
        name = syn.getTeam(participantid)['name']
      else:
        participantid = sub.userId
        name = syn.getUserProfile(participantid)['userName']
      evaluation = syn.getEvaluation(sub.evaluationId)
      message = subject = ""
      if args.status == "INVALID":
        subject = f"Submission to '{evaluation.name}' is Invalid"
        message = [f"Hello {name},\n\n",
                   f"Your submission (ID: {sub.id}) to Task 1 is invalid for the following reasons:\n\n\t",
                   args.invalid.replace(
                    "RARE-X Organizers",
                    "<a href='https://www.synapse.org/#!Team:3468097'>RARE-X Organizers</a>"
                   ),
                   "\n\nPlease try again once the issues are addressed.",
                   "\n\nThank you,\nRARE-X Challenge Organizers"]
      else:
        subject = f"Submission to '{evaluation.name}' Accepted"
        message = [f"Hello {name},\n\n",
                   f"Your submission (ID: {sub.id}) to Task 1 passed validation and is now pending ",
                   "review/judging.  Note that you may continue editing the submitted writeup up until ",
                   "the submission deadline; no re-submissions are required.  After the submission ",
                   "deadline, our panel of judges will review the latest wiki version of the writeup, ",
                   "and results will be announced at a later time.\n\n",
                   "Thank you for your participation! \n\n",
                   "Sincerely,\nRARE-X Challenge Organizers"]
      if message:
        syn.sendMessage(
          userIds=[participantid],
          messageSubject=subject,
          messageBody="".join(message))

inputs:
- id: submissionid
  type: int
- id: synapse_config
  type: File
- id: status
  type: string
- id: invalid_reasons
  type: string

outputs:
- id: finished
  type: boolean
  outputBinding:
    outputEval: $( true )

baseCommand: python3
arguments:
- valueFrom: send_email.py
- prefix: -s
  valueFrom: $(inputs.submissionid)
- prefix: -c
  valueFrom: $(inputs.synapse_config.path)
- prefix: --status
  valueFrom: $(inputs.status)
- prefix: -i
  valueFrom: $(inputs.invalid_reasons)

hints:
  DockerRequirement:
    dockerPull: sagebionetworks/synapsepythonclient:v2.7.2

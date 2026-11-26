# Example: Consultant role limit email

Sent 2026-10-28 to Pat Okafor (EA ED). Two data-entry issues at the
Acuity booking stage caused mis-attached training records in Airtable.

## What this example demonstrates for voice-align

- Full sentences throughout, no fragments standing in for sentences.
- First useful point comes first. The orienting line ("Here are two issues
  I found today") is one sentence, not a preview paragraph.
- Each sentence carries one fact. Francisco's phone, Lorena's record, the
  sync rule, the result each sit in their own sentence.
- Bullets use dot leaders for plain lists. The arrow `→` annotates a bullet
  with a related fact. Both are preserved formats.
- No metaphors. "Attached to Lorena" is literal. The word "attached" matches
  how Airtable renders a linked record relationship. No "clean," "catch,"
  "slip," "stuck in the pipe."
- No em dashes. Commas, colons, and sentence breaks carry every pause.
- No throat-clearing opener. No "I wanted to let you know." The greeting is
  one friendly line, then the first useful point.
- Material facts stay in one place. The sync-by-phone rule is stated once
  in the Francisco section, not restated as a summary at the end.
- No ending summary. The last paragraph adds a new fact (the consultant-role
  limit and the open-door invitation), not a recap.

## The email

Hi Pat,

I hope you're having a good week so far. Here are two issues I found today. Both of them involve adding clients in Acuity without enough information. This led to downstream data problems in Airtable. I caught and corrected it this time, but it will prevent correct training tracking if not caught.

For example, Alonso was added in Acuity with these issues:
. His phone was saved as "1+5628053071" instead of "+15628053071"
. His email was empty
. His "Tipo de cliente" (Client Type) was empty
. He got booked into Modules 5 and 6, which are the post-approval classes, even though he is still on the pre-approval track
→ Both of Alonso's bookings were made from person7@example.com. One was on October 23. The other was on October 26.

For a record like Alonso's to come in correctly, the booking in Acuity needs these four things:
. Phone in the +1XXXXXXXXXX shape, with no "1+" at the front
. Email filled in
. "Tipo de cliente" picked
. The right module for the client status, either pre-approval or post-approval

I recorded a short video for whoever is doing the bookings. It shows how to fill each of these in as well as going over how to use the dashboard. [staff video link] Below is a screenshot from Acuity that tells us who is signing up people for trainings.

Problem 2

Francisco booked tonight's Module 1 five times. He cancelled four of them, and one is still active.

Francisco used his household phone number, +13236786958. That phone number is already saved on Lorena's record. It is not saved on Francisco's. Airtable connects each new booking to an applicant by looking at the phone number. Because the phone number pointed to Lorena, all five of Francisco's bookings were attached to Lorena.

Lorena already finished Module 1 on October 21. If I had left tonight's booking attached to her, the trainer would mark her present. The credit would count toward Lorena instead of Francisco. Francisco would still look like he had not done Module 1. I moved those five rows over to Francisco. Nothing else on the rows changed.

When a household has two applicants who share one phone number, the applicant and co-applicant need to decide which of them will use that phone number. Please don't put the same phone number in for two different people because it could impact whether or not they are correctly credited for their training.

Would you want me to build a report that shows any new records with these kinds of issues as they come in? Your team would see them in one place.

The second part is a dashboard where EA staff would be able to add or correct phone number, client type, and other information.

Would it help if I built the report and the page for you? Either way works for me. I just want to make sure your team feels good about it.

In my role as your consultant, fixing records by hand isn't a good use of the hours you have with me, so I'm going to stop going back to correct these one at a time. The system we went over last week is the way to add people to training. If anyone is getting stuck, I'd rather hear that and fix the system than keep fixing the records. And if I'm missing something about why this keeps coming up, I'm open to hearing it.

All best,
Rachael

Rachael Quisel
Workflow Consultant, XRAY

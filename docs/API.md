# API Reference

The base URL is `VITE_API_URL` (default: `http://127.0.0.1:5000`). Frontend calls use Axios with `/api` as the base path and credentials enabled.

## Authentication

| Method | Route | Description | Required role |
|---|---|---|---|
| POST | `/api/auth/signup` | Register a normal user or submit an authority application | Public |
| POST | `/api/auth/login` | Log in and set the JWT access cookie | Public |
| GET | `/api/auth/me` | Return the current identity and role | Authenticated |
| POST | `/api/auth/logout` | Clear the JWT cookie | Public |

## Admin

| Method | Route | Description | Required role |
|---|---|---|---|
| GET | `/api/admin/authorities` | List authority applications | Admin |
| GET | `/api/admin/authorities/<authority_id>` | Inspect an authority application | Admin |
| PATCH | `/api/admin/authorities/<authority_id>/status` | Set an authority to pending, approved, or rejected and send email | Admin |
| GET | `/api/admin/dashboard-stats` | Get pending-authority and monthly report counts | Admin |

## Missing-person reports

| Method | Route | Description | Required role |
|---|---|---|---|
| POST | `/api/missing-report/send` | Submit a missing-person report and run face matching | User; Admin is also accepted by the backend role logic |
| POST | `/api/report/<match_id>/validate` | Confirm or reject an uncertain match owned by the user | User |
| GET | `/api/my-missing-cases` | List owned missing-person reports | User |
| DELETE | `/api/my-missing-cases/<missing_id>` | Delete an owned missing-person report | User |
| PUT | `/api/my-missing-cases/<missing_id>` | Update an owned missing-person report | User |
| GET | `/api/my-missing-match/<match_id>` | Inspect an owned missing-report match | User |
| PATCH | `/api/my-missing-match/<match_id>/confirm` | Confirm an uncertain match | User |
| PATCH | `/api/my-missing-match/<match_id>/reject` | Reject an uncertain match | User |

## Found-person reports

| Method | Route | Description | Required role |
|---|---|---|---|
| POST | `/api/found-report/send` | Submit a found-person report and run face matching | Authority or Admin |
| POST | `/api/found-report/<match_id>/validate` | Confirm or reject an uncertain match owned by the authority/admin | Authority or Admin |
| GET | `/api/my-found-cases` | List owned found-person reports | Authority or Admin |
| DELETE | `/api/my-found-cases/<found_id>` | Delete an owned found-person report | Authority or Admin |
| PUT | `/api/my-found-cases/<found_id>` | Update an owned found-person report | Authority or Admin |
| GET | `/api/found-match/<match_id>` | Inspect a match owned by the authority/admin | Authority or Admin |
| PATCH | `/api/found-match/<match_id>/cancel` | Cancel a match owned by the authority/admin | Authority or Admin |
| PATCH | `/api/found-match/<match_id>/confirm` | Confirm an uncertain owned match | Authority or Admin |
| PATCH | `/api/found-match/<match_id>/reject` | Reject an uncertain owned match | Authority or Admin |

## Missing-person database

| Method | Route | Description | Required role |
|---|---|---|---|
| GET | `/api/missing-database` | List missing-person records and match status | Authority or Admin |
| GET | `/api/missing-database/<missing_id>` | Inspect a missing-person record | Authority or Admin |
| DELETE | `/api/missing-database/<missing_id>` | Delete a missing-person record | Admin |
| GET | `/api/missing-database-match/<match_id>` | Inspect missing-database match details | Authority or Admin |
| PATCH | `/api/missing-database-match/<match_id>/cancel` | Cancel a missing-database match | Admin |

## Found-person database

| Method | Route | Description | Required role |
|---|---|---|---|
| GET | `/api/found-database` | List found-person records and match status | Admin |
| GET | `/api/found-database/<found_id>` | Inspect a found-person record | Admin |
| DELETE | `/api/found-database/<found_id>` | Delete a found-person record | Admin |
| GET | `/api/found-database-match/<match_id>` | Inspect found-database match details | Admin |
| PATCH | `/api/found-database-match/<match_id>/cancel` | Cancel a found-database match | Admin |

## Normal-user profile

| Method | Route | Description | Required role |
|---|---|---|---|
| GET | `/api/user-profile` | Get the normal-user profile | Normal user |
| PUT | `/api/user-profile/info` | Update the normal-user profile | Normal user |
| PUT | `/api/user-profile/password` | Change the normal-user password | Normal user |

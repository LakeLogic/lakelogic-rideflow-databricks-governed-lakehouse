# Synthetic data generator bundle (LakeLogic Synthetic v2)

Source: lakehouse design bp:snap-7ca870d1dda142db r1
Generated at: revision:chv1:2fc51b81bdf6952ee34e50711d632f4547e2880e5e610273bc83991ae7f38f50 seal:sha256:bb8a338dcef1c410b29f3593a4b9208a2a067e37192afef793154074fe379973
Generator: lakelogic DataGenerator v1.88.0

## Fidelity profile: contract-derived

This bundle ships a **deterministic seeded generator**, not synthetic rows. It was built
from the contract **schemas only** — **no production rows were read** — so it can be shared
freely: no synthetic data crosses a boundary until *you* run `generate.py` locally.

Values are contract-derived: the generator uses semantic hints from column names (email,
name, phone, address, ...) and type-correct fakes otherwise. This is NOT profile- or
sample-informed fidelity (those are later, separately-governed modes); no distribution or
value from your production data informs these fakes.

## Permanent synthetic classification

Every artifact produced by this bundle is **synthetic, permanently** (ADR-0011 decision 6:
synthetic is not the same as anonymised). Do not re-classify generated data as production.

## PII / masked columns

Columns flagged `pii` / `sensitive` in the contracts carry a `masking` strategy. Run the
generated frames through `lakelogic.DataProcessor(<contract>).run(df)` to apply masking by
construction (`redact` -> `***REDACTED***`, `hash` -> pseudonym). The generator emits
semantically-shaped fakes for these columns; it never emits a real identifier.

## Staged rollout (use synthetic BEFORE real data)

Run any exported pipeline against THIS synthetic data first, staged:
`dry_run` -> `ddl_only` -> `live` — validate the design on synthetic before pointing it at
production. Injected-invalid rows (`invalid_ratio=0.0`) let you prove your
quality gates quarantine bad rows.

## Contents

  - `generate.py` — the standalone generator (needs `pip install lakelogic`)
  - `config.json` — the pinned config (seed, rows, window, relationships)
  - `contracts/*.yaml` — the contracts (deterministically serialized, once; the canonical source of truth)

## Config

  - seed: 7
  - rows_per_table: 100
  - invalid_ratio: 0.0
  - window: 2020-01-01T00:00:00 .. 2025-01-01T00:00:00 (module default)

## Tables

  - bronze_checkr_driver_licences
  - bronze_checkr_driver_verifications
  - bronze_google_ads_campaigns
  - bronze_google_analytics_app_events
  - bronze_google_analytics_sessions
  - bronze_hubspot_email_campaigns
  - bronze_hubspot_push_notifications
  - bronze_internal_cities
  - bronze_internal_fx_rates_daily
  - bronze_meta_ads_campaigns
  - bronze_rideflow_driver_profiles
  - bronze_rideflow_driver_telemetry
  - bronze_rideflow_rider_app_events
  - bronze_rideflow_rider_profiles
  - bronze_rideflow_trip_cancellations
  - bronze_rideflow_trip_requests
  - bronze_rideflow_trips
  - bronze_stripe_charges
  - bronze_stripe_payouts
  - bronze_stripe_refunds
  - bronze_twilio_sms_logs
  - bronze_zendesk_support_tickets
  - gold_dim_cancel_reason_code
  - gold_dim_cancelled_by
  - gold_dim_cities
  - gold_dim_date
  - gold_dim_driver_licences
  - gold_dim_driver_profiles
  - gold_dim_driver_telemetry_status
  - gold_dim_preferred_payment_method
  - gold_dim_rider_profiles
  - gold_dim_rider_profiles_status
  - gold_dim_trip_type
  - gold_fact_app_events
  - gold_fact_app_events_daily
  - gold_fact_charges
  - gold_fact_charges_daily
  - gold_fact_driver_telemetry
  - gold_fact_driver_telemetry_daily
  - gold_fact_driver_verifications
  - gold_fact_email_campaigns
  - gold_fact_fx_rates_daily
  - gold_fact_payouts
  - gold_fact_payouts_daily
  - gold_fact_push_notifications
  - gold_fact_refunds
  - gold_fact_refunds_daily
  - gold_fact_rider_app_events
  - gold_fact_sms_logs
  - gold_fact_sms_logs_daily
  - gold_fact_support_tickets
  - gold_fact_support_tickets_daily
  - gold_fact_trip_cancellations
  - gold_fact_trip_cancellations_daily
  - gold_fact_trip_requests
  - gold_fact_trip_requests_daily
  - gold_fact_trips
  - gold_fact_trips_daily
  - gold_google_ads_fact_campaigns
  - gold_google_ads_fact_campaigns_daily
  - gold_meta_ads_fact_campaigns
  - gold_meta_ads_fact_campaigns_daily
  - gold_rideflow_dim_event_name
  - gold_rideflow_dim_platform
  - silver_checkr_driver_licences
  - silver_checkr_driver_verifications
  - silver_google_ads_campaigns
  - silver_google_analytics_app_events
  - silver_google_analytics_sessions
  - silver_hubspot_email_campaigns
  - silver_hubspot_push_notifications
  - silver_internal_cities
  - silver_internal_fx_rates_daily
  - silver_meta_ads_campaigns
  - silver_rideflow_driver_profiles
  - silver_rideflow_driver_telemetry
  - silver_rideflow_rider_app_events
  - silver_rideflow_rider_profiles
  - silver_rideflow_trip_cancellations
  - silver_rideflow_trip_requests
  - silver_rideflow_trips
  - silver_stripe_charges
  - silver_stripe_payouts
  - silver_stripe_refunds
  - silver_twilio_sms_logs
  - silver_zendesk_support_tickets

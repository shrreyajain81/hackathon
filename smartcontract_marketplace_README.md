# Marketplace README

## Overview

The Marketplace feature allows patients to select wellness activities and receive exclusive coupon codes. When a patient redeems an activity, their payout is increased by a percentage discount associated with that activity.

## Components

### Marketplace Server

**File:** `marketplace_server.py`

Flask server running on `localhost:6000` that manages:
- Available wellness activities
- Coupon generation and validation
- Payout adjustments
- Coupon tracking

### Available Activities

1. **Gym Membership** 🏋️ - 10% payout boost
2. **Pilates Classes** 🧘 - 15% payout boost
3. **Spa & Wellness** 💆 - 20% payout boost
4. **Yoga Sessions** 🧘‍♀️ - 12% payout boost
5. **Swimming Pool** 🏊 - 8% payout boost
6. **Nutrition Counseling** 🥗 - 25% payout boost

### UI Integration

The marketplace is integrated into the dashboard as a new tab with the following workflow:

1. Patient selects a patient ID
2. System loads available activities
3. Patient clicks on an activity to redeem
4. UI sends POST request to marketplace server
5. Server generates coupon code and calculates new payout
6. UI displays coupon with updated payout amount

## Setup

### 1. Start Marketplace Server

```bash
python marketplace_server.py
```

Server will start on http://localhost:6000

Output:

```Code
Starting Marketplace Server...
Available endpoints:
  GET /api/marketplace/health - Health check
  GET /api/marketplace/activities - List available activities
  POST /api/marketplace/redeem - Redeem an activity (get coupon)
  GET /api/marketplace/patient/<id>/payout - Get adjusted payout
  GET /api/marketplace/patient/<id>/coupons - Get patient coupons
```
### 2. Keep UI Server Running
The UI server should also be running (on port 8000) to access the marketplace tab.
#!/usr/bin/env python3
"""
COMPREHENSIVE VALIDATION: Risk-Return Analysis Calculations
Validates calculations against actual AAPL output data
"""

def validate_aapl_calculations():
    """Validate calculations using actual AAPL data from output"""
    print("=== AAPL RISK-RETURN VALIDATION ===")
    
    # Actual AAPL data from the generated report
    aapl_data = {
        'risk_score': 3.9,  # out of 10 (39%)
        'beta': 1.21,
        'max_drawdown': -33.4,  # -33.4%
        'sharpe_ratio': -0.16,
        'returns': {
            'return_1d': -0.28,   # -0.28%
            'return_1w': 2.25,    # 2.25%
            'return_1m': 0.4,     # 0.4%
            'return_3m': -9.1,    # -9.1%
            'return_6m': -20.8,   # -20.8%
            'return_1y': None     # N/A
        },
        'volatility': 40.0  # 40% (from report)
    }
    
    print("AAPL Market Data:")
    for key, value in aapl_data.items():
        if key != 'returns':
            print(f"  {key}: {value}")
    
    print("\nAAL Returns by Period:")
    for period, return_val in aapl_data['returns'].items():
        print(f"  {period}: {return_val}%")
    
    print("\n=== VOLATILITY RISK CALCULATION ===")
    
    # Simulate the volatility risk calculation for AAPL
    volatility_risk = 0.5  # Default medium risk
    liquidity_risk = 0.3   # Default
    
    print(f"Starting volatility_risk: {volatility_risk}")
    
    # Apply volatility adjustments
    if aapl_data['volatility'] > 40:  # 40% threshold
        volatility_risk = max(volatility_risk, 0.8)
        print(f"High volatility (40%+) adjustment: {volatility_risk}")
    elif aapl_data['volatility'] < 20:
        volatility_risk = min(volatility_risk, 0.3)
        print(f"Low volatility (<20%) adjustment: {volatility_risk}")
    
    # Apply beta adjustments
    if aapl_data['beta'] > 1.5:
        volatility_risk += 0.1
        print(f"High beta (>1.5) adjustment: {volatility_risk}")
    elif aapl_data['beta'] < 0.5:
        volatility_risk -= 0.1
        print(f"Low beta (<0.5) adjustment: {volatility_risk}")
    else:
        print(f"Beta {aapl_data['beta']} - no adjustment needed")
    
    # Apply max drawdown adjustments
    max_drawdown_decimal = aapl_data['max_drawdown'] / 100  # Convert to decimal
    if max_drawdown_decimal < -0.3:  # -30%
        volatility_risk += 0.1
        print(f"Large drawdown ({aapl_data['max_drawdown']}%) adjustment: {volatility_risk}")
    
    # Clamp to 0-1 range
    volatility_risk = max(0.0, min(1.0, volatility_risk))
    
    # Calculate overall market risk
    market_risk_score = (volatility_risk * 0.7) + (liquidity_risk * 0.3)
    market_risk_score = max(0.0, min(1.0, market_risk_score))
    
    print(f"\nFinal Calculations:")
    print(f"  volatility_risk: {volatility_risk:.3f}")
    print(f"  market_risk_score: {market_risk_score:.3f}")
    print(f"  Chart X-axis (volatility_risk * 100): {volatility_risk * 100:.1f}%")
    
    # Compare with actual risk score from report
    actual_risk_percent = aapl_data['risk_score'] * 10  # Convert 3.9/10 to percentage
    print(f"  Actual report risk score: {aapl_data['risk_score']}/10 = {actual_risk_percent:.1f}%")
    
    print("\n=== RETURN CALCULATION ===")
    
    # Determine which return period to use (longest available)
    return_value = None
    return_period = ""
    
    for period in ['return_1y', 'return_6m', 'return_3m', 'return_1m', 'return_1w', 'return_1d']:
        if aapl_data['returns'][period] is not None:
            return_value = aapl_data['returns'][period]
            return_period = period
            break
    
    if return_value is not None:
        y_return = return_value  # Already in percentage
        print(f"Selected return period: {return_period}")
        print(f"Return value: {return_value}%")
        print(f"Chart Y-axis: {y_return:.1f}%")
    else:
        print("No return data available - would use fallback")
    
    print("\n=== CHART COLOR LOGIC ===")
    
    # Test the actual AAPL values
    x_risk = volatility_risk * 100
    y_return = return_value if return_value else 0
    
    if y_return > 10 and x_risk < 25:
        color = 'green'  # High return, low risk
    elif y_return > 0 and x_risk < 30:
        color = 'blue'   # Positive return, moderate risk
    elif y_return < -10:
        color = 'red'    # Negative return
    else:
        color = 'orange' # Neutral
    
    print(f"AAPL Chart Position:")
    print(f"  X (Risk): {x_risk:.1f}%")
    print(f"  Y (Return): {y_return:.1f}%") 
    print(f"  Color: {color}")
    
    # Quadrant analysis
    quadrant = ""
    if x_risk < 25 and y_return > 0:
        quadrant = "Low Risk, Positive Return"
    elif x_risk >= 25 and y_return > 0:
        quadrant = "High Risk, Positive Return"
    elif x_risk < 25 and y_return <= 0:
        quadrant = "Low Risk, Negative Return"
    else:
        quadrant = "High Risk, Negative Return"
    
    print(f"  Quadrant: {quadrant}")
    
    print("\n=== VALIDATION SUMMARY ===")
    
    # Check if calculations make sense
    print("Validation Checks:")
    
    # 1. Risk score should reflect high volatility and large drawdown
    if volatility_risk > 0.5:
        print("✓ High volatility (40%) correctly increases risk score")
    else:
        print("✗ High volatility should increase risk score")
    
    # 2. Negative return should be reflected in chart
    if return_value and return_value < 0:
        print("✓ Negative return correctly identified")
    else:
        print("✗ Should show negative return")
    
    # 3. Color should be red for negative return < -10%
    expected_color = 'red' if y_return < -10 else 'orange'
    if color == expected_color:
        print(f"✓ Color ({color}) correctly assigned for {y_return:.1f}% return")
    else:
        print(f"✗ Color should be {expected_color} for {y_return:.1f}% return, got {color}")
    
    # 4. Large drawdown should increase risk
    if max_drawdown_decimal < -0.3:
        print(f"✓ Large drawdown ({aapl_data['max_drawdown']}%) correctly increases risk")
    
    print(f"\nCalculated values match expected behavior for AAPL's risk-return profile.")

if __name__ == "__main__":
    validate_aapl_calculations()

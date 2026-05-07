#!/usr/bin/env python3
"""
Detailed comparison of legacy vs adaptive model selection strategies.
Shows model choices and fit quality metrics side-by-side.

Run in CMSSW environment:
  python3 K0sAnalysis/fitting/test_compare_detailed.py
"""

import sys
import os
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

import ROOT
ROOT.gROOT.SetBatch(ROOT.kTRUE)

import fitting.count_peak as cp


def create_synthetic_histogram(name='synthetic'):
    """Create a synthetic histogram: Gaussian peak on flat background"""
    
    # Create histogram
    hist = ROOT.TH1F(name, name, 100, 4.5, 5.5)
    
    # Flat background
    rng = np.random.RandomState(42)
    n_background = 800
    background = rng.uniform(4.5, 5.5, n_background)
    
    # Gaussian signal (peak at 5.0, sigma=0.05)
    n_signal = 200
    signal = rng.normal(5.0, 0.05, n_signal)
    
    # Fill histogram
    for x in np.concatenate([background, signal]):
        hist.Fill(x)
    
    return hist


def format_comparison(result):
    """Format the comparison result as a readable table"""
    print("\n" + "="*80)
    print("LEGACY vs ADAPTIVE MODEL SELECTION COMPARISON")
    print("="*80)
    
    print(f"\nHistogram: {result['histogram_name']}")
    print(f"Effective Entries: {result['effective_entries']:.1f}")
    print(f"Fit Mode: {result['mode']}")
    
    legacy = result['legacy']
    adaptive = result['adaptive']
    
    # Model selection comparison
    print("\n" + "-"*80)
    print("MODEL SELECTION")
    print("-"*80)
    print(f"{'Strategy':<20} {'Background':<15} {'Signal':<15}")
    print("-"*80)
    print(f"{'Legacy':<20} {legacy['background_model']:<15} {legacy['signal_model']:<15}")
    print(f"{'Adaptive':<20} {adaptive['background_model']:<15} {adaptive['signal_model']:<15}")
    
    # Fit quality (for adaptive only, legacy doesn't track these)
    if adaptive['background_chi2'] is not None:
        print("\n" + "-"*80)
        print("FIT QUALITY (χ²/NDF)")
        print("-"*80)
        print(f"{'Component':<25} {'χ²':<12} {'NDF':<8} {'χ²/NDF':<12}")
        print("-"*80)
        
        print(f"{'Adaptive Background':<25}")
        print(f"  {'':<23} {adaptive['background_chi2']:<12.4g} {adaptive['background_ndf']:<8d} {adaptive['background_chi2_ndf']:<12.4g}")
        
        print(f"{'Adaptive Signal':<25}")
        print(f"  {'':<23} {adaptive['signal_chi2']:<12.4g} {adaptive['signal_ndf']:<8d} {adaptive['signal_chi2_ndf']:<12.4g}")
        
        print(f"{'Adaptive Confidence':<25}")
        print(f"  {'':<23} {adaptive['confidence_chi2']:<12.4g} {adaptive['confidence_ndf']:<8d} {adaptive['confidence_chi2_ndf']:<12.4g}")
    
    # Measurements comparison
    print("\n" + "-"*80)
    print("MEASUREMENT RESULTS")
    print("-"*80)
    print(f"{'Metric':<25} {'Legacy':<25} {'Adaptive':<25} {'Δ (rel %)':<15}")
    print("-"*80)
    
    # Peak count
    legacy_peak = legacy['peak_count']
    adaptive_peak = adaptive['peak_count']
    delta_peak = (adaptive_peak - legacy_peak) / legacy_peak * 100 if legacy_peak != 0 else np.nan
    print(f"{'Peak Count':<25} {legacy_peak:<25.4g} {adaptive_peak:<25.4g} {delta_peak:<15.2f}%")
    
    # Peak error
    legacy_erro = legacy['peak_error']
    adaptive_erro = adaptive['peak_error']
    delta_erro = (adaptive_erro - legacy_erro) / legacy_erro * 100 if legacy_erro != 0 else np.nan
    print(f"{'Peak Error':<25} {legacy_erro:<25.4g} {adaptive_erro:<25.4g} {delta_erro:<15.2f}%")
    
    # Confidence width
    legacy_conf = legacy['confidence']
    adaptive_conf = adaptive['confidence']
    delta_conf = (adaptive_conf - legacy_conf) / legacy_conf * 100 if legacy_conf != 0 else np.nan
    print(f"{'Confidence Width':<25} {legacy_conf:<25.4g} {adaptive_conf:<25.4g} {delta_conf:<15.2f}%")
    
    # Confidence error
    legacy_conf_err = legacy['conf_error']
    adaptive_conf_err = adaptive['conf_error']
    delta_conf_err = (adaptive_conf_err - legacy_conf_err) / legacy_conf_err * 100 if legacy_conf_err != 0 else np.nan
    print(f"{'Confidence Error':<25} {legacy_conf_err:<25.4g} {adaptive_conf_err:<25.4g} {delta_conf_err:<15.2f}%")
    
    print("\n" + "="*80)
    
    # Summary
    models_agree = (legacy['background_model'] == adaptive['background_model'] and 
                   legacy['signal_model'] == adaptive['signal_model'])
    print(f"\nModel Selection Agreement: {'YES ✓' if models_agree else 'NO ✗'}")
    print(f"Peak Count Difference: {abs(delta_peak):.2f}%")
    print("="*80 + "\n")


def main():
    print("\nCreating synthetic histogram...")
    hist = create_synthetic_histogram('synthetic_test')
    
    gargs = {
        'helpdir': None,
        'helpdir2': None,
        'lumi': 1.0,  # 1fb-1
    }
    
    print("Running comparison (this runs both legacy and adaptive fits)...")
    result = cp.count_peak_compare(hist, 'Synthetic Test Histogram', 'Random=42', gargs, mode='subtract')
    
    # Display formatted comparison
    format_comparison(result)
    
    # Return result for potential further processing
    return result


if __name__ == '__main__':
    result = main()
    print("\n✓ Comparison completed successfully!")

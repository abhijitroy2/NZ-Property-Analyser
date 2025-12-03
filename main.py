"""
Main entry point for NZ Property Analyser
"""
import argparse
import sys
import os
from datetime import datetime
from typing import List
from logger import setup_logger
from property_processor import process_properties
from config import DEFAULT_EMAIL

# Input folder path
INPUT_FOLDER = "input"

# Set up initial logger (will be reconfigured with file-specific log later)
logger = setup_logger(__name__)


def get_email_address(foreground_mode: bool) -> str:
    """
    Get email address based on mode.
    
    Args:
        foreground_mode: True if foreground mode, False if background mode
        
    Returns:
        Email address string
    """
    if foreground_mode:
        email = input("Please enter your email address: ").strip()
        if not email:
            logger.warning("No email provided, using default")
            return DEFAULT_EMAIL
        return email
    else:
        logger.info(f"Background mode: Using default email {DEFAULT_EMAIL}")
        return DEFAULT_EMAIL


def main():
    """Main function to run the property analyser."""
    parser = argparse.ArgumentParser(
        description="NZ Property Analyser - Analyze property investments in flip or rental mode"
    )
    
    parser.add_argument(
        'files',
        nargs='+',
        help='One or more Excel files containing property data'
    )
    
    parser.add_argument(
        '--mode',
        choices=['flip', 'rental'],
        default='flip',
        help='Calculation mode: flip or rental (default: flip)'
    )
    
    parser.add_argument(
        '--background',
        action='store_true',
        help='Run in background mode (uses default email)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output Excel file path (optional, auto-generated if not provided)'
    )
    
    args = parser.parse_args()
    
    # Ensure input folder exists
    os.makedirs(INPUT_FOLDER, exist_ok=True)
    
    # Process file paths - if relative, look in input folder
    processed_file_paths = []
    for file_path in args.files:
        if os.path.isabs(file_path):
            # Absolute path, use as-is
            processed_file_paths.append(file_path)
        else:
            # Relative path, check in input folder first
            input_path = os.path.join(INPUT_FOLDER, file_path)
            if os.path.exists(input_path):
                processed_file_paths.append(input_path)
            elif os.path.exists(file_path):
                # File exists in current directory
                processed_file_paths.append(file_path)
            else:
                # Try input folder anyway
                processed_file_paths.append(input_path)
    
    # Generate log file name based on first input file
    if processed_file_paths:
        first_file = processed_file_paths[0]
        # Extract base filename without extension
        base_name = os.path.splitext(os.path.basename(first_file))[0]
        # Add timestamp to make it unique
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file_name = f"{base_name}_{timestamp}.log"
    else:
        log_file_name = f"property_analyser_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Reconfigure logger with file-specific log file (before any logging)
    logger = setup_logger(__name__, log_file=log_file_name)
    
    # Determine mode
    foreground_mode = not args.background
    
    # Get email address
    email = get_email_address(foreground_mode)
    logger.info(f"Email address: {email}")
    
    # Process files
    try:
        
        logger.info("=" * 60)
        logger.info("NZ Property Analyser - Starting Processing")
        logger.info("=" * 60)
        logger.info(f"Log file: {log_file_name}")
        
        result_df = process_properties(
            file_paths=processed_file_paths,
            mode=args.mode,
            output_file=args.output
        )
        
        logger.info("=" * 60)
        logger.info("Processing completed successfully!")
        logger.info("=" * 60)
        
        # Display summary
        total_properties = len(result_df)
        
        if args.mode == "flip":
            if 'Is_Good_Deal' in result_df.columns:
                good_deals = len(result_df[result_df['Is_Good_Deal'] == True])
            else:
                good_deals = 0
            logger.info(f"Total properties processed: {total_properties}")
            logger.info(f"Good deals found: {good_deals}")
        else:  # rental
            if 'Is_Successful' in result_df.columns:
                successful = len(result_df[result_df['Is_Successful'] == True])
            else:
                successful = 0
            logger.info(f"Total properties processed: {total_properties}")
            logger.info(f"Successful rental properties: {successful}")
        
        if 'Has_Stress_Keywords' in result_df.columns:
            stress_sales = len(result_df[result_df['Has_Stress_Keywords'] == True])
        else:
            stress_sales = 0
        logger.info(f"Properties with stress keywords: {stress_sales}")
        
        # Note: Email functionality skipped per user preference
        logger.info("Email functionality skipped (per configuration)")
        
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()


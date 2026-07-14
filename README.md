# Sample QRcode Generator
This app takes as input a single file with at least one column (the first row should be named `sample_ID`).
When you upload your file, the app will generate QR codes for each sample ID within the input file.

**NOTE:** For CSV files, make sure that the separator is a `comma (,)`, not a `semicolon (;)`.
For TSV files, make sure that the separator is a `tab`.
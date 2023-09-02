# IRIS export extractor

This script extracts items from an InterSystems
[IRIS](https://www.intersystems.com/data-platform/) XML export file.

Source code items are generally exported individually, in UDL format
(i.e., mostly like you see the source in Studio or VS Code). The XML
export format still has advantages, though. Most importantly, it can
combine source code items into a single export file. This can make
deployment of code easier in some workflows.

This script can extract items from such an XML export, and create a new
export containing only those items. This can be useful to create a
partial export with limited functionality.

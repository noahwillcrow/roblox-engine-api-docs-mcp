<p align="center">
<img src="https://github.com/MaximumADHD/Roblox-Client-Tracker/assets/3926900/ff0ba96d-e133-48a8-8541-80fc6ca21f52">
</p>

<hr/>

# What is this?

The **Roblox Client Tracker** is an unofficial change tracker which aims to provide detailed difflogs for changes to Roblox's engine. It generates information by datamining builds of Roblox Studio retrieved from their CDN, using various publicly discovered developer channels of Roblox. The data that is analyzed and presented in this repository is generated using publicly reverse engineered Roblox protocols and file formats.

# Source Code

The backend console application which drives this repository is available to be found here:<br/>
https://github.com/MaximumADHD/RCT-Source

# Specifications

## API-Dump.json
This is a JSON version of Roblox's API Dump. It contains more data than the original API Dump and can be read into a data tree by most programming languages using a JSON parser. This file is extracted using:<br/>`RobloxStudioBeta.exe -API API-Dump.json`

## Full-API-Dump.json
This is a more *"complete"* version of the normal JSON API Dump. It includes all classes and enums omitted from the normal dump, and includes a few other notable differences and keys, like `Default` values on some properties. This file can be extracted with, similarly to `-API`:<br/>`RobloxStudioBeta.exe -FullAPI Full-API-Dump.json`

## API-Dump.txt
A readable version of Roblox's JSON API Dump. This file is generated from the [Roblox API Dump Tool](https://github.com/MaximumADHD/Roblox-API-Dump-Tool).

## CppTree.txt
A sorted list of undecorated C++ symbol names that could be extracted from the exe.

## DeepStrings.txt
A sorted list of dumped strings from Roblox Studio's exe. There is *some* garbage data dumped into this file, but most of it should be legible.

## EmulatedDevices.xml
A file used by Roblox Studio which defines the specifications, platforms, and images for all default emulation devices.

## FVariables.txt
A sorted list of fast variables, which are used by Roblox to toggle changes to the engine remotely on multiple platforms without having to redeploy the client.

## RobloxShaderData.csv
This CSV maps all of Roblox's known shaders, and which graphics APIs use them. Each mapped shader has a mapped name and shader-type.

## rbxManifest.txt
A file that describes (almost) every file that is expected to be extracted from the zip files specified in rbxPkgManifest.txt
Every two lines of this file corresponds to a local file path, and the MD5 checksum expected of the file extracted to that path.

This file is fetched at:<br/>
`https://setup.rbxcdn.com/{version-$guid}-rbxManifest.txt`<br/>
`https://setup.rbxcdn.com/channel/{channelName}/{version-$guid}-rbxManifest.txt`

## rbxPkgManifest.txt
A file that describes which zip files should be fetched from Roblox's Amazon S3 bucket.

This file can be fetched at:<br/>
`https://setup.rbxcdn.com/{version-$guid}-rbxPkgManifest.txt`<br/>
`https://setup.rbxcdn.com/channel/{channelName}/{version-$guid}-rbxPkgManifest.txt`

The file starts with a line describing the version for the package manifest schema.
After the version, information about each file is listed sequentually as such:

```
File.ext
MD5 Checksum
Compressed Size
Decompressed Size
```

These files are fetched at:<br/>
`https://setup.rbxcdn.com/{version-$guid}-rbxPkgManifest.txt`<br/>
`https://setup.rbxcdn.com/channel/{channelName}/{version-$guid}-{FileName}`

## rbxManifest.csv
A CSV version of `rbxManifest.txt`, made to be easier to read from GitHub.

## rbxPkgManifest.csv
A CSV version of `rbxPkgManifest.txt`, made to be easier to read from GitHub.

## version.txt
Describes the current version of Roblox Studio.<br/>
Formatted as: **(MajorRevision).(Version).(Patch).(Changelist)**

## version-guid.txt
Describes the current GUID version of Roblox Studio.
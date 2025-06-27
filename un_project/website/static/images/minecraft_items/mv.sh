#!/bin/bash
for file in minecraft_*; do
    mv "$file" "${file#minecraft_}"
done

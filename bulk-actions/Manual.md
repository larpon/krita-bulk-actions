# Bulk Actions

A Krita plugin for bulk actions and operations on multiple marked layers.

This plugin provides a sort of layer "tag" functionality.
You "tag" each layer with a character or string - allowing the plugin to identify
layers as a collection or group across spread across the layer tree.

You can then perform different actions on these "tagged" layers at once.
It is possible to use some supported unicode characters as tags (e.g. ⭕, 👁 or ⭮) to keep layer names as
uncluttered as possible.

This is especially convenient if you have a layers you want to switch on and off often spread across
the layer tree.

## Example
You have character with different body parts and those body parts have layers for shadows.
You want to be able to see the character with and without the effect of your shadows.
You then simply mark those layers with a character i.e: "@" in the layer name and then setup a
bulk action for changing their visibility:
```
Root
  +-- Robot
  |    |
  |    +-- Head
  |    |     |
  |    |     +-- Outline
  |    |     +-- Shadows @     <-- This is the marked layer
  |    |     +-- Color
  |    |
  |    +-- Body
  |    |     |
  |    |     +-- Outline
  |    |     +-- Shadows @     <-- This is the marked layer
  |    |     +-- Color
  |    |
  |    +-- Legs
  |          |
  |          +-- Outline
  |          +-- Shadows @     <-- This is the marked layer
  |          +-- Color
  |
  |
  Background
```

You then click the Add Action: `+` in the Bulk Actions dock.
Then select `Visible` in the ComboBox and type `@` in the input field.

Pressing enter in the input field or clicking the checkmark button will then toggle the visibility of those layers.

You can add as many actions as you like with as many marks you like.

You can save and load your settings within each Krita document `.kra` file.
At this point Krita's scripting API don't allow for any user/script data to be stored within the document - so the plugin will store
it's data in a layer inside the layer tree called "Plugin Settings". You can move the layer around the tree and change it's state - but you
can't delete it or rename it without the settings being cleared.

## Demo
You can also see a quick [demo video](https://youtu.be/wTWlr6GYXBQ) of the plugin in action.

Happy bulk actioning!

# Krita Bulk Actions

A Krita plugin for bulk actions and operations on multiple marked layers.

This plugin provides a sort of layer "tag" functionality.
You "tag" each layer with a character or string - allowing the plugin to identify
layers as a collection or group spread across the layer tree.

You can then perform different actions on these "tagged" layers at once.
It is possible to use some supported unicode characters as tags (e.g. ⭕, 👁 or ⭮) to keep layer names as
uncluttered as possible.

This is especially convenient if you have a layers you want to switch on and off often spread across
the layer tree.

## Install
You install the plugin by placing the `bulk-action` folder and `bulk-action.desktop` file from this repository in your `pykrita` folder. You can find the `pykrita` folder in the menu by going to *Settings -> Manage Resources...* and press the *Open Resources Folder* button.

Once placed the plugin docker can be activated via *Settings -> Dockers -> Bulk Actions*

## Supported layer actions

Leaving the `pattern` field empty will result in matching currently selected layers

Set a value for the following attributes:

* Opacity
* Name

Toggle the following attributes:

* Visible
* Locked
* Alpha Locked
* Collapsed state
* Inherit Alpha

## Usage
To add actions use the icons after "Add action".

Your actions will be applied to the currently *selected* layers if you leave the `pattern` field *empty*
**otherwise** the action will be applied to the layers *matching* the pattern in the `pattern` field (available with each action).
The `pattern` field is for each action only - no other layers will be touched.

For modifying actions such as layer renaming - you will be able to see, and accept, the modifications before they're applied!

### Applying an action

* Click the leftmost icon of an action entry.

### Removing an action

* Click the rightmost icon (`-`) of an action entry.

### Saving actions
To save your actions with each `.kra` document you need to have an open document, then:

* Press the "Save" button in the bottom part of the docker
* Remember to save your document as well, when appropriate.

### Loading actions

* Press the "Load" button in the bottom part of the docker.

### Clearing actions

* Press the "Clear" button in the bottom part of the docker.

See Notes below for more technical details on saving and loading.


## Examples

### Toggling visibility
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


## Demo
You can also see a quick [demo video](https://youtu.be/wTWlr6GYXBQ) of the plugin in action.

## Notes
Due to the current state of Krita's scripting API there's a few things to notice:

* When saving plugin settings you need to save your `.kra` document as well!
    * Krita will not detect when the settings changed you can force "change" by doing: `Ctrl+a` -> `Ctrl+Shift+a`
* Krita's scripting API don't allow for any user/script data to be stored within the document
    * The plugin will store it's data in a layer inside the layer tree called "Plugin Settings".
    * You can move the layer around the tree and change it's state
    * You can't delete it or rename it without the settings being unreadable.
* For saving of visibility states **only** I have been notified of [Compositions](https://docs.krita.org/en/reference_manual/dockers/compositions.html) which does much the same as "Visible" settings will do in this plugin.

Happy bulk actioning!

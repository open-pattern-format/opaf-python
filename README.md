# Open Pattern Format (OPAF)

`OPAF` is a comprehensive pattern file format aimed at yarn based crafts including knitting and crochet. The pattern is defined using a custom XML like syntax and can be compiled to a true XML interpretation using the `opaf` tool.

Patterns are built using `blocks` where components, rows or individual pattern repeats are defined and called on as necessary in your main pattern definition. You can define configurable values for things like stitch count and use math expressions and conditions throughout to generate bespoke patterns based on size, gauge or other parameters.

##  Features

* Value definitions
* Block definitions for pattern repeats
* Math expressions
* Conditions
* Common `actions` pre-defined
* Define your own `actions`
* Python API

### OPAF basic template

```xml
<pattern name="My Awesome Pattern" >
    <component name="my_first_component" >
        <round>
            <opaf_actions ... />
        </round>
    </component>
    <component name="my_second_component" >
        <row>
            <opaf_actions ... />
        </row>
    </component>
</pattern>
```

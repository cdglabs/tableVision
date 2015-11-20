
# =============================================================================
# Model
# =============================================================================

model = window.model = new class
  constructor: ->
    @sourceFiles = [] # {fileName, content}
    @logEntries = [] # {fileName, lineNumber, image}
    @selectedFileName = false

  selectedFile: ->
    return @sourceFiles.find (sourceFile) =>
      sourceFile.fileName == @selectedFileName

  selectFile: (fileName) ->
    @selectedFileName = fileName

  reload: ->
    @reloadSourceFiles()
    @reloadLogEntries()

  reloadSourceFiles: ->
    @fetchJson "/sourceFiles.json", (data) =>
      @sourceFiles = data
      if !@selectedFileName
        @selectedFileName = @sourceFiles[0].fileName
      render()

  reloadLogEntries: ->
    @fetchJson "/logEntries.json", (data) =>
      @logEntries = data
      render()
      refreshAnnotations()

  fetchJson: (url, callback) ->
    fetch(url)
      .then (response) -> response.json()
      .then (data) -> callback(data)

  save: ->
    data = {
      sourceFiles: @sourceFiles
      currentFileName: @selectedFileName
    }
    fetch("/save", {
      method: "post"
      headers: {
        "Accept": "application/json"
        "Content-Type": "application/json"
      }
      body: JSON.stringify(data)
    }).then (response) =>
      @reloadLogEntries()


# =============================================================================
# (Re)rendering the View
# =============================================================================

render = ->
  contentEl = document.querySelector("#content")
  R.render(R.App(), contentEl)

refreshAnnotations = ->
  for el in document.querySelectorAll(".SourceCode")
    el.refreshAnnotations()


# =============================================================================
# R: Convenience API into React
# =============================================================================

R = window.R = {}

# Provide easy access to React.DOM
for own key, value of React.DOM
  R[key] = value

# Utility (from React.addons.classSet)
R.cx = (classNames) ->
  Object.keys(classNames).filter((className) -> classNames[className]).join(" ")

R.create = (name, spec) ->
  # Component.displayName is used by React in its debugging messages.
  spec.displayName = name
  component = React.createClass(spec)
  R[name] = React.createFactory(component)

R.render = ReactDOM.render
R.findDOMNode = ReactDOM.findDOMNode


# =============================================================================
# Views
# =============================================================================

R.create "App",
  render: ->
    R.div {},
      R.div {className: "Files"},
        for sourceFile in model.sourceFiles
          R.File {sourceFile, key: sourceFile.fileName}
        R.button {onClick: @addFile}, "Add"
      R.div {className: "SourceCodes"},
        for sourceFile in model.sourceFiles
          R.SourceCode {sourceFile, key: sourceFile.fileName}
  addFile: ->
    fileName = prompt("File Name")
    model.sourceFiles.push {fileName, content: ""}
    model.selectFile(fileName)
    render()

R.create "File",
  render: ->
    {fileName, content} = @props.sourceFile
    isSelected = (fileName == model.selectedFileName)
    R.div {
      className: R.cx {
        "File": true
        "Selected": isSelected
      }
      onClick: @onClick
    },
      R.div {className: "FileName"}, fileName
      R.div {className: "FileImages"},
        for logEntry in model.logEntries
          if logEntry.fileName == fileName
            R.img {src: "/log/" + logEntry.image, key: logEntry.image}

  onClick: ->
    {fileName, content} = @props.sourceFile
    model.selectFile(fileName)
    render()


R.create "SourceCode",
  render: ->
    {fileName, content} = @props.sourceFile
    isSelected = (fileName == model.selectedFileName)
    R.div {
      className: R.cx {
        "SourceCode": true
        "Selected": isSelected
      }
    }

  componentDidMount: ->
    el = R.findDOMNode(this)

    el.refreshAnnotations = @refreshAnnotations

    @mirror = CodeMirror(el, {
      mode: "python"
      theme: "material"
      keyMap: "sublime"

      smartIndent: true
      indentUnit: 4
      # scrollPastEnd: true # Helps with not losing your place when refresh log images...

      matchBrackets: true
      autoCloseBrackets: true
      styleActiveLine: true

      lineNumbers: true
      extraKeys: {
        # Indent with spaces, not tabs.
        "Tab": (cm) ->
          spaces = Array(cm.getOption("indentUnit") + 1).join(" ")
          cm.replaceSelection(spaces)
        "Cmd-S": =>
          model.save()
      }
    })

    @initializeContent()

    @mirror.on("change", @onChange)

  initializeContent: ->
    sourceFile = @props.sourceFile
    @mirror.setValue(sourceFile.content)
    @refreshAnnotations()

  refreshAnnotations: ->
    sourceFile = @props.sourceFile

    # Clear existing widgets
    for lineNumber in [0 ... @mirror.lineCount()]
      {widgets} = @mirror.lineInfo(lineNumber)
      for widget in widgets ? []
        widget.clear()
    # @mirror.setValue(@mirror.getValue())

    for logEntry in model.logEntries
      {fileName, lineNumber, image} = logEntry
      if fileName == sourceFile.fileName
        imgEl = document.createElement("img")
        imgEl.src = "/log/" + image
        lineText = @mirror.getLine(lineNumber)
        indent = lineText.replace(/[^ ].*/, "").length
        imgEl.style.marginLeft = indent * 9 + "px"
        widget = @mirror.addLineWidget(lineNumber-1, imgEl)
        # When image loads, need to tell the widget that we changed height.
        imgEl.addEventListener "load", ->
          widget.changed()

  onChange: ->
    sourceFile = @props.sourceFile

    sourceFile.content = @mirror.getValue()


# =============================================================================
# Bootstrap
# =============================================================================

model.reload()

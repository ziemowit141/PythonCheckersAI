import Tkinter
import copy
import random
import time
from Tkinter import *
from checkerPiece import CheckerPiece


class CheckerBoard(Canvas):
    gb = Tkinter.Tk()
    greyPieces = []
    redPieces = []
    board = []
    highlightedTiles = []
    currentlySelectedCheckerObject = CheckerPiece(0, 0, "grey", False, 0)
    currentlySelectedCheckerID = 0
    tileWidth = 31
    tileHeight = 31
    rows = 8
    columns = 8
    GREY_CHECKER = 1
    RED_CHECKER = 2
    tileBorder = .75
    checkerBorder = 4
    currentPlayer = "red"
    mustDoubleJump = False
    redCount = 12
    greyCount = 12
    redScoreBoard = Label(gb, text="Red: %i" % redCount)
    greyScoreBoard = Label(gb, text="Grey: %i" % greyCount)

    # min_max addition
    temporaryGreyPieces = []
    temporaryRedPieces = []
    min_max_active_flag = False

    # Description: Start a new game. Reset all checkers to starting position
    def startNewGame(self):
        # Delete all checkers
        for i in self.greyPieces:
            self.delete(i[0])
        for i in self.redPieces:
            self.delete(i[0])

        # Delete all arrays storing checkers. (not the board array. That stores game tiles)
        for i in range(0, len(self.greyPieces)):
            self.greyPieces.pop()

        for i in range(0, len(self.redPieces)):
            self.redPieces.pop()

        for i in range(0, len(self.highlightedTiles)):
            self.highlightedTiles.pop()

        # Reset all variables (not reseting board)
        self.greyPieces = []
        self.redPieces = []
        self.highlightedTiles = []
        self.currentlySelectedCheckerObject = CheckerPiece(0, 0, "grey", False, 0)
        self.currentlySelectedCheckerID = 0
        self.currentPlayer = "red"
        self.mustDoubleJump = False
        self.redCount = 12
        self.greyCount = 12
        self.redScoreBoard.config(text="Red: %i" % self.redCount)
        self.greyScoreBoard.config(text="Grey: %i" % self.greyCount)

        # Make new checkers
        self.createCheckers()

    # Description: Initializes main window, canvas, tiles, and checkers
    # Creates main window, canvas, tiles, and checkers
    def __init__(self):
        self.gb.minsize(250, 350)
        Canvas.__init__(self, self.gb, bg="grey", height=250, width=250)
        newGameButton = Button(self.gb, text="New Game", command=self.startNewGame)
        self.redScoreBoard.pack()
        self.greyScoreBoard.pack()
        self.pack()
        newGameButton.pack()
        self.createTiles()
        self.createCheckers()
        self.gb.mainloop()

    # Description: Function creates red and black tiles for the game board
    def createTiles(self):
        width = self.tileWidth
        height = self.tileHeight
        for i in range(0, self.columns):
            x1 = (i * width) + self.tileBorder
            x2 = ((i + 1) * width) - self.tileBorder
            for j in range(0, self.rows):
                y1 = (j * height) + self.tileBorder
                y2 = ((j + 1) * height) - self.tileBorder
                if (i + j) % 2 == 0:
                    idVal = self.create_rectangle(x1, y1, x2, y2, fill="red")
                else:
                    idVal = self.create_rectangle(x1, y1, x2, y2, fill="black")
                if idVal != 0:
                    self.board.append((idVal, j, i, x1, x2, y1, y2))

    # Description: Function places all checkers on the game board at their starting positions
    def createCheckers(self):
        checkerWidth = self.tileWidth
        checkerHeight = self.tileWidth
        # Iterate over each row. Row indicates y position
        for i in range(0, self.rows):
            # No checkers are placed on the 3rd or 4th row, so continue to the next row in loop if i == 3 or 4
            if i == 3 or i == 4:
                continue
            # Calculate y1 and y2 of the oval that forms the checker
            y1 = (i * checkerWidth) + self.checkerBorder
            y2 = ((i + 1) * checkerWidth) - self.checkerBorder
            # Grey checkers are placed on rows 0-2
            if i < 3:
                checkerColor = "grey"
            # Red checkers are placed on rows 5-7
            elif i > 4:
                checkerColor = "red"
            # Iterate over each column in the row. Column indicates x position
            for j in range(0, self.columns):
                # If the sum of the row(i) and column(j) is odd, a checker should go in this cell
                if (i + j) % 2 == 1:
                    # Calculate x1 and x2 of the oval that forms the checker
                    x1 = (j * checkerHeight) + self.checkerBorder
                    x2 = ((j + 1) * checkerHeight) - self.checkerBorder
                    # Draw the checker on the board, giving it a color tag and an id tag
                    idTag = self.create_oval(x1, y1, x2, y2, fill=checkerColor)
                    self.tag_bind(idTag, "<ButtonPress-1>", self.processCheckerClick)
                    # Create a checker object to keep track of this newly created checker
                    newChecker = CheckerPiece(i, j, checkerColor, False, idTag)
                    # Append the id and checker object to their proper arrays
                    if checkerColor == "grey":
                        self.greyPieces.append((idTag, newChecker))
                    elif checkerColor == "red":
                        self.redPieces.append((idTag, newChecker))

    # Description: Process the user clicking a checker
    def processCheckerClick(self, event):
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        idValue = self.find_closest(x, y)[0]
        selectedChecker = self.getCheckerObject(idValue)
        # If selectedChecker == 0, the idValue passed to getCheckerObject does not match any known idValues
        if selectedChecker == 0:
            return
        # Only process click if currentPlayer == selectedChecker's color
        if (self.currentPlayer == selectedChecker.getColor()) and self.mustDoubleJump is False:
            # Assign the currentlySelectedCheckerObject and currentlySelectedCheckerID
            self.currentlySelectedCheckerObject = selectedChecker
            self.currentlySelectedCheckerID = idValue
            # Reset all highlighted tiles
            self.resetHighlightedTiles()
            # Show all available moves for the selected checker
            self.showAllAvailableRegularMoves(selectedChecker)
            # Show all available jump moves for the selected checker
            self.showAllAvailableJumpMoves(selectedChecker)

    # Description: process the user selecting a highlighted tile
    def processHighlightedTileClicked(self, event):
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        idValue = self.find_closest(x, y)[0]
        # Find the new row and column to move the currently selected checker to
        newRow = 100
        newCol = 100
        jumpedCheckerID = 0
        for i in self.board:
            if i[0] == idValue:
                newRow = i[1]
                newCol = i[2]
                jumpedCheckerID = self.getJumpedCheckerID(newRow, newCol)
                break
        # If newRow == 100, invalid tile was selected
        if newRow == 100:
            return

        # Move the currently selected checker to the tile with the selected idVal
        self.moveCurrentlySelectedChecker(newRow, newCol)
        # Reset all highlighted tiles
        self.resetHighlightedTiles()
        # If the selected checker made a jump, remove the jumped checker, show the current checker more jump moves
        if jumpedCheckerID != 0:
            self.removeChecker(jumpedCheckerID)
            self.showAllAvailableJumpMoves(self.currentlySelectedCheckerObject)
            # If there are jumps left for the player, set the mustDoubleJump flag to true
            if len(self.highlightedTiles) > 0:
                self.mustDoubleJump = True
            # Else if there are no jumps left for the player, set the mustDoubleJump flag to false and switch players
            else:
                self.switchCurrentPlayer()
                self.mustDoubleJump = False
        # If the selected checker was just a normal move, switch players
        else:
            self.switchCurrentPlayer()

    # Description: Switch the current player to the next player
    def switchCurrentPlayer(self):
        if self.currentPlayer == "red":
            self.currentPlayer = "grey"
            self.AI_move()
        elif self.currentPlayer == "grey":
            self.currentPlayer = "red"

    # Description: Remove checker from the board and its respective checker array
    def removeChecker(self, checkerID):
        if checkerID != 0:
            self.delete(checkerID)
            for i in self.redPieces:
                if i[0] == checkerID:
                    self.redPieces.remove(i)
                    self.redCount = self.redCount - 1
                    self.redScoreBoard.config(text="Red: %i" % self.redCount)
                    break
            for i in self.greyPieces:
                if i[0] == checkerID:
                    self.greyPieces.remove(i)
                    self.greyCount = self.greyCount - 1
                    self.greyScoreBoard.config(text="Grey: %i" % self.greyCount)
                    break
            self.checkForWin()

    # Description: Remove checker from the board and its respective checker array
    def removeChecker_2(self, checkerID, pieces):
        if checkerID != 0:
            for i in pieces:
                if i[0] == checkerID:
                    pieces.remove(i)
                    break

    # Description: Check if red or grey has won. If so, congratulate them
    def checkForWin(self):
        if self.redCount <= 0:
            greyWinnerLabel = Label(self.gb, text="Grey Wins!")
            greyWinnerLabel.pack()
            self.stopTheGame()
        elif self.greyCount <= 0:
            redWinnerLabel = Label(self.gb, text="Red Wins!")
            redWinnerLabel.pack()
            self.stopTheGame()

    # Description: Stops the game by unbinding all events
    def stopTheGame(self):
        for i in self.redPieces:
            checkerIDVal = i[0]
            if checkerIDVal != 0:
                self.tag_unbind(checkerIDVal, "<ButtonPress-1>")
        for i in self.greyPieces:
            checkerIDVal = i[0]
            if checkerIDVal != 0:
                self.tag_unbind(checkerIDVal, "<ButtonPress-1>")
        self.resetHighlightedTiles()

    # Description: given row and column, get jumped checker id
    def getJumpedCheckerID(self, row_, col_):
        for i in self.highlightedTiles:
            if row_ == i[0] and col_ == i[1]:
                return i[2]
        return 0

    # Description: move the currently selected checker to (newRow_, newCol_)
    def moveCurrentlySelectedChecker(self, newRow_, newCol_):
        y1 = (newRow_ * self.tileWidth) + self.checkerBorder
        y2 = ((newRow_ + 1) * self.tileWidth) - self.checkerBorder
        x1 = (newCol_ * self.tileWidth) + self.checkerBorder
        x2 = ((newCol_ + 1) * self.tileWidth) - self.checkerBorder
        # Move checker to new location
        self.coords(self.currentlySelectedCheckerID, (x1, y1, x2, y2))
        # Update currentlySelectedChecker's location
        self.currentlySelectedCheckerObject.updateLocation(newRow_, newCol_)
        if self.currentlySelectedCheckerObject.isKing():
            self.itemconfig(self.currentlySelectedCheckerID, outline="cyan")

    # Description: move the currently selected checker to (newRow_, newCol_)
    def moveChosenChecker(self, checker, newRow_, newCol_):
        y1 = (newRow_ * self.tileWidth) + self.checkerBorder
        y2 = ((newRow_ + 1) * self.tileWidth) - self.checkerBorder
        x1 = (newCol_ * self.tileWidth) + self.checkerBorder
        x2 = ((newCol_ + 1) * self.tileWidth) - self.checkerBorder
        # Move checker to new location
        self.coords(checker[0], (x1, y1, x2, y2))
        # Update currentlySelectedChecker's location
        checker[1].updateLocation(newRow_, newCol_)
        if checker[1].isKing():
            self.itemconfig(checker[0], outline="cyan")

    # Description: reset all highlighted tiles to black borders instead of yellow
    #                unbind all events the highlighted tiles had
    def resetHighlightedTiles(self):
        # Reset all currently highlighted cells
        for i in self.highlightedTiles:
            tileIDVal = self.getTileID(i[0], i[1])
            if tileIDVal != 0:
                self.itemconfig(tileIDVal, outline="black")
                self.tag_unbind(tileIDVal, "<ButtonPress-1>")

        # Remove all current values from highlightedTiles
        for i in range(0, len(self.highlightedTiles)):
            self.highlightedTiles.pop()

    # Description: show available moves for a selected checker
    def showAllAvailableRegularMoves(self, _selectedChecker):
        selectedChecker = _selectedChecker
        selectedCheckerIsKing = selectedChecker.isKing()
        selectedCheckerColor = selectedChecker.getColor()
        openSpaces = []

        if selectedCheckerIsKing:
            # Check north west neighbor
            rowValue = selectedChecker.getNWneighbor()[0]
            colValue = selectedChecker.getNWneighbor()[1]
            if not self.isTileOccupied(rowValue, colValue)[0]:
                openSpaces.append(selectedChecker.getNWneighbor())

            # Check north east neighbor
            rowValue = selectedChecker.getNEneighbor()[0]
            colValue = selectedChecker.getNEneighbor()[1]
            if not self.isTileOccupied(rowValue, colValue)[0]:
                openSpaces.append(selectedChecker.getNEneighbor())

            # Check south west neighbor
            rowValue = selectedChecker.getSWneighbor()[0]
            colValue = selectedChecker.getSWneighbor()[1]
            if not self.isTileOccupied(rowValue, colValue)[0]:
                openSpaces.append(selectedChecker.getSWneighbor())

            # Check south east neighbor
            rowValue = selectedChecker.getSEneighbor()[0]
            colValue = selectedChecker.getSEneighbor()[1]
            if not self.isTileOccupied(rowValue, colValue)[0]:
                openSpaces.append(selectedChecker.getSEneighbor())
        # Else if checker is normal and red, only check north west and north east
        elif selectedCheckerColor == "red":
            # Check north west neighbor
            rowValue = selectedChecker.getNWneighbor()[0]
            colValue = selectedChecker.getNWneighbor()[1]
            if not self.isTileOccupied(rowValue, colValue)[0]:
                openSpaces.append(selectedChecker.getNWneighbor())

            # Check north east neighbor
            rowValue = selectedChecker.getNEneighbor()[0]
            colValue = selectedChecker.getNEneighbor()[1]
            if not self.isTileOccupied(rowValue, colValue)[0]:
                openSpaces.append(selectedChecker.getNEneighbor())
            # print(openSpaces)
        # Else if checker is normal and grey, only check south west and south east
        elif selectedCheckerColor == "grey":
            # Check south west neighbor
            rowValue = selectedChecker.getSWneighbor()[0]
            colValue = selectedChecker.getSWneighbor()[1]
            if not self.isTileOccupied(rowValue, colValue)[0]:
                openSpaces.append(selectedChecker.getSWneighbor())

            # Check south east neighbor
            rowValue = selectedChecker.getSEneighbor()[0]
            colValue = selectedChecker.getSEneighbor()[1]
            if not self.isTileOccupied(rowValue, colValue)[0]:
                openSpaces.append(selectedChecker.getSEneighbor())

        # Highlight all open spaces
        if self.currentPlayer == 'red':
            for i in range(0, len(openSpaces)):
                highlightRow = openSpaces[i][0]
                highlightCol = openSpaces[i][1]
                if highlightRow == 100 or highlightCol == 100:
                    continue
                tileIDVal = self.getTileID(highlightRow, highlightCol)
                if tileIDVal != 0:
                    self.itemconfig(tileIDVal, outline="yellow")
                    self.tag_bind(tileIDVal, "<ButtonPress-1>", self.processHighlightedTileClicked)
                    self.highlightedTiles.append((highlightRow, highlightCol, 0))
                else:
                    print "Invalid tile"

        return openSpaces

    # Description: Show all available jump moves a selected checker can make
    def showAllAvailableJumpMoves(self, selectedChecker_):
        selectedChecker = selectedChecker_
        selectedCheckerIsKing = selectedChecker.isKing()
        selectedCheckerColor = selectedChecker.getColor()
        available_jump_moves = []

        if selectedCheckerIsKing:
            # Check north west neighbor
            rowValue = selectedChecker.getNWneighbor()[0]
            colValue = selectedChecker.getNWneighbor()[1]
            isTileOccupiedReturnArray = self.isTileOccupied(rowValue, colValue)
            isTileOccupied = isTileOccupiedReturnArray[0]
            tileColor = isTileOccupiedReturnArray[1]
            jumpCheckerID = isTileOccupiedReturnArray[2]
            if isTileOccupied:
                if selectedCheckerColor != tileColor:
                    jumpRow = selectedChecker.getNWneighbor()[0]
                    jumpCol = selectedChecker.getNWneighbor()[1]
                    self.checkForJump(jumpRow - 1, jumpCol - 1, jumpCheckerID)
                    move = self.checkForJump(jumpRow - 1, jumpCol - 1, jumpCheckerID)
                    if move is not None:
                        available_jump_moves.append(move)

            # Check north east neighbor
            rowValue = selectedChecker.getNEneighbor()[0]
            colValue = selectedChecker.getNEneighbor()[1]
            isTileOccupiedReturnArray = self.isTileOccupied(rowValue, colValue)
            isTileOccupied = isTileOccupiedReturnArray[0]
            tileColor = isTileOccupiedReturnArray[1]
            jumpCheckerID = isTileOccupiedReturnArray[2]
            if isTileOccupied:
                if selectedCheckerColor != tileColor:
                    jumpRow = selectedChecker.getNEneighbor()[0]
                    jumpCol = selectedChecker.getNEneighbor()[1]
                    self.checkForJump(jumpRow - 1, jumpCol + 1, jumpCheckerID)
                    move = self.checkForJump(jumpRow - 1, jumpCol + 1, jumpCheckerID)
                    if move is not None:
                        available_jump_moves.append(move)

            # Check south west neighbor
            rowValue = selectedChecker.getSWneighbor()[0]
            colValue = selectedChecker.getSWneighbor()[1]
            isTileOccupiedReturnArray = self.isTileOccupied(rowValue, colValue)
            isTileOccupied = isTileOccupiedReturnArray[0]
            tileColor = isTileOccupiedReturnArray[1]
            jumpCheckerID = isTileOccupiedReturnArray[2]
            if isTileOccupied:
                if selectedCheckerColor != tileColor:
                    jumpRow = selectedChecker.getSWneighbor()[0]
                    jumpCol = selectedChecker.getSWneighbor()[1]
                    self.checkForJump(jumpRow + 1, jumpCol - 1, jumpCheckerID)
                    move = self.checkForJump(jumpRow + 1, jumpCol - 1, jumpCheckerID)
                    if move is not None:
                        available_jump_moves.append(move)

            # Check south east neighbor
            rowValue = selectedChecker.getSEneighbor()[0]
            colValue = selectedChecker.getSEneighbor()[1]
            isTileOccupiedReturnArray = self.isTileOccupied(rowValue, colValue)
            isTileOccupied = isTileOccupiedReturnArray[0]
            tileColor = isTileOccupiedReturnArray[1]
            jumpCheckerID = isTileOccupiedReturnArray[2]
            if isTileOccupied:
                if selectedCheckerColor != tileColor:
                    jumpRow = selectedChecker.getSEneighbor()[0]
                    jumpCol = selectedChecker.getSEneighbor()[1]
                    self.checkForJump(jumpRow + 1, jumpCol + 1, jumpCheckerID)
                    move = self.checkForJump(jumpRow + 1, jumpCol + 1, jumpCheckerID)
                    if move is not None:
                        available_jump_moves.append(move)

        # Else if checker is a normal, red checker, check the north west and north east neighbors
        elif selectedCheckerColor == "red":
            # Check north west neighbor
            rowValue = selectedChecker.getNWneighbor()[0]
            colValue = selectedChecker.getNWneighbor()[1]
            isTileOccupiedReturnArray = self.isTileOccupied(rowValue, colValue)
            isTileOccupied = isTileOccupiedReturnArray[0]
            tileColor = isTileOccupiedReturnArray[1]
            jumpCheckerID = isTileOccupiedReturnArray[2]
            if isTileOccupied:
                if selectedCheckerColor != tileColor:
                    jumpRow = selectedChecker.getNWneighbor()[0]
                    jumpCol = selectedChecker.getNWneighbor()[1]
                    move = self.checkForJump(jumpRow - 1, jumpCol - 1, jumpCheckerID)
                    if move is not None:
                        available_jump_moves.append(move)

            # Check north east neighbor
            rowValue = selectedChecker.getNEneighbor()[0]
            colValue = selectedChecker.getNEneighbor()[1]
            isTileOccupiedReturnArray = self.isTileOccupied(rowValue, colValue)
            isTileOccupied = isTileOccupiedReturnArray[0]
            tileColor = isTileOccupiedReturnArray[1]
            jumpCheckerID = isTileOccupiedReturnArray[2]
            if isTileOccupied:
                if selectedCheckerColor != tileColor:
                    jumpRow = selectedChecker.getNEneighbor()[0]
                    jumpCol = selectedChecker.getNEneighbor()[1]
                    move = self.checkForJump(jumpRow - 1, jumpCol + 1, jumpCheckerID)
                    if move is not None:
                        available_jump_moves.append(move)

        elif selectedCheckerColor == "grey":
            # Check south west neighbor
            rowValue = selectedChecker.getSWneighbor()[0]
            colValue = selectedChecker.getSWneighbor()[1]
            isTileOccupiedReturnArray = self.isTileOccupied(rowValue, colValue)
            isTileOccupied = isTileOccupiedReturnArray[0]
            tileColor = isTileOccupiedReturnArray[1]
            jumpCheckerID = isTileOccupiedReturnArray[2]
            if isTileOccupied:
                if selectedCheckerColor != tileColor:
                    jumpRow = selectedChecker.getSWneighbor()[0]
                    jumpCol = selectedChecker.getSWneighbor()[1]
                    move = self.checkForJump(jumpRow + 1, jumpCol - 1, jumpCheckerID)
                    if move is not None:
                        available_jump_moves.append(move)

            # Check south east neighbor
            rowValue = selectedChecker.getSEneighbor()[0]
            colValue = selectedChecker.getSEneighbor()[1]
            isTileOccupiedReturnArray = self.isTileOccupied(rowValue, colValue)
            isTileOccupied = isTileOccupiedReturnArray[0]
            tileColor = isTileOccupiedReturnArray[1]
            jumpCheckerID = isTileOccupiedReturnArray[2]
            if isTileOccupied:
                if selectedCheckerColor != tileColor:
                    jumpRow = selectedChecker.getSEneighbor()[0]
                    jumpCol = selectedChecker.getSEneighbor()[1]
                    move = self.checkForJump(jumpRow + 1, jumpCol + 1, jumpCheckerID)
                    if move is not None:
                        available_jump_moves.append(move)

        return available_jump_moves

    # Description: Highlight square if jump tile is not occupied
    def checkForJump(self, row_, col_, jumpedCheckerID_):
        # If row_ and col_ are not on the board, return
        if not self.isValidPosition(row_, col_):
            return None
        # If tile is not occupied, highlight it
        if not self.isTileOccupied(row_, col_)[0]:
            tileIDVal = self.getTileID(row_, col_)
            if tileIDVal != 0:
                self.itemconfig(tileIDVal, outline="yellow")
                self.tag_bind(tileIDVal, "<ButtonPress-1>", self.processHighlightedTileClicked)
                self.highlightedTiles.append((row_, col_, jumpedCheckerID_))
                return row_, col_, jumpedCheckerID_

    # Description: Checks if tile described by the rowVal and colVal is occupied
    #                If occupied, returns (True, <colorOfCheckerOccupyingTheTile> , <idOfCheckerOccupyingTheTile>)
    #                If not occupied, returns (False, "NA", 0)
    def isTileOccupied(self, rowVal, colVal):
        row = rowVal
        col = colVal

        if self.min_max_active_flag is False:
            if not self.isValidPosition(row, col):
                return False, "NA", 0

            # Check if any grey checkers are in the tile
            for i in range(0, len(self.greyPieces)):
                currentChecker = self.greyPieces[i][1]
                if (row == currentChecker.getRow()) and (col == currentChecker.getColumn()):
                    return True, "grey", self.greyPieces[i][0]

            # Check if any red checkers are in the tile
            for i in range(0, len(self.redPieces)):
                currentChecker = self.redPieces[i][1]
                if (row == currentChecker.getRow()) and (col == currentChecker.getColumn()):
                    return True, "red", self.redPieces[i][0]

        else:
            if not self.isValidPosition(row, col):
                return False, "NA", 0

            # Check if any grey checkers are in the tile
            for i in range(0, len(self.temporaryGreyPieces)):
                currentChecker = self.temporaryGreyPieces[i][1]
                if (row == currentChecker.getRow()) and (col == currentChecker.getColumn()):
                    return True, "grey", self.temporaryGreyPieces[i][0]

            # Check if any red checkers are in the tile
            for i in range(0, len(self.temporaryRedPieces)):
                currentChecker = self.temporaryRedPieces[i][1]
                if (row == currentChecker.getRow()) and (col == currentChecker.getColumn()):
                    return True, "red", self.temporaryRedPieces[i][0]
        # No checkers found in the tile, return (False, "NA", 0)
        return False, "NA", 0

    # Description: returns the checker object representing the passed id value
    def getCheckerObject(self, idValue):
        # Check greyPieces for id
        for i in range(0, len(self.greyPieces)):
            if self.greyPieces[i][0] == idValue:
                return self.greyPieces[i][1]

        # Check redPieces for id
        for i in range(0, len(self.redPieces)):
            if self.redPieces[i][0] == idValue:
                return self.redPieces[i][1]

        # If no checker found, return 0
        return 0

    def getCheckerObject_2(self, checkers, idValue):
        # Check greyPieces for id
        for i in range(0, len(checkers)):
            if checkers[i][0] == idValue:
                return checkers[i][1]

        # Check redPieces for id
        for i in range(0, len(checkers)):
            if checkers[i][0] == idValue:
                return checkers[i][1]

        # If no checker found, return 0
        return 0

    # Description: Return the tileID of the tile found at (row_, col_)
    def getTileID(self, row_, col_):
        row = row_
        col = col_
        for i in range(0, len(self.board)):
            if row == self.board[i][1] and col == self.board[i][2]:
                return self.board[i][0]
        return 0

    # Description: Return true if the position is valid
    def isValidPosition(self, row_, col_):
        return self.isValidRow(row_) and self.isValidColumn(col_)

    # Description: Return true if the row is valid
    def isValidRow(self, row_):
        if row_ >= 0 and row_ <= 7:
            return True
        else:
            return False

    # Description: Return true if the col is valid
    def isValidColumn(self, col_):
        if col_ >= 0 and col_ <= 7:
            return True
        else:
            return False

    def evaluate_positions(self, greyPices):
        evaluation_score = 0
        for piece in greyPices:
            if piece[1].getRow() == 3:
                evaluation_score += 15
            elif 0 <= piece[1].getRow() < 3:
                evaluation_score += 10
            elif piece[1].getRow() > 3:
                evaluation_score += 5

        return evaluation_score

    def AI_jump_move(self):
        jump_moves = self.get_all_movable_pieces_and_their_jump_moves(self.greyPieces)
        for piece, moves in jump_moves:
            if len(moves) > 0:
                move = random.choice(moves)
                self.moveChosenChecker(piece, move[0], move[1])
                self.removeChecker(move[2])
                self.AI_jump_move()

    def AI_move(self):
        # movablePieces = self.get_all_movable_pieces_and_their_jump_moves(self.greyPieces)
        start = time.time()
        piece_id, move, eval = self.min_max_def(self.redPieces, self.greyPieces, 4, False)
        end = time.time()
        print(end - start)
        print("Choosen move is: " + str(move))
        print(eval)
        piece = self.getCheckerObject_2(self.greyPieces, piece_id)
        self.moveChosenChecker((piece_id, piece), move[0], move[1])
        if len(move) == 3:
            self.removeChecker(move[2])
            self.AI_jump_move()
        self.switchCurrentPlayer()

    def get_all_movable_pieces_and_their_jump_moves(self, pieces):
        movablePieces = []
        for piece in pieces:
            available_moves = self.showAllAvailableJumpMoves(piece[1])
            if len(available_moves) > 0:
                available_moves = [move for move in available_moves if move[0] != 100 and move[1] != 100]
                if len(available_moves) > 0:
                    movablePieces.append((piece, available_moves))

        return movablePieces

    def get_all_movable_pieces_and_their_regular_moves(self, pieces):
        movablePieces = []
        for piece in pieces:
            available_moves = self.showAllAvailableRegularMoves(piece[1])
            if len(available_moves) > 0:
                available_moves = [move for move in available_moves if move[0] != 100 and move[1] != 100]
                if len(available_moves) > 0:
                    movablePieces.append((piece, available_moves))

        return movablePieces

    def simulate_move(self, piece, move):
        piece[1].updateLocation(move[0], move[1])

    def simulate_jump_move(self, piece, move, pieces):
        self.removeChecker_2(move[2], pieces)
        piece[1].updateLocation(move[0], move[1])

    def min_max(self, red_pieces, grey_pieces, depth, maximizingPlayer, alfa, beta):
        if depth == 0 or len(red_pieces) == 0 or len(grey_pieces) == 0:
            return 0, 0, len(red_pieces)

        best_piece = (0, 0)
        best_move = (100, 100)
        if maximizingPlayer:
            evals = []
            maxEval = float('-inf')
            jump_moves = self.get_all_movable_pieces_and_their_jump_moves(red_pieces)
            if len(jump_moves) > 0:
                for piece, moves in jump_moves:
                    for move in moves:
                        red_pieces_copy = copy.deepcopy(red_pieces)
                        grey_pieces_copy = copy.deepcopy(grey_pieces)
                        piece_to_move = self.getCheckerObject_2(red_pieces_copy, piece[0])
                        self.simulate_jump_move((piece[0], piece_to_move), move, grey_pieces_copy)
                        _, _, eval = self.min_max(red_pieces_copy, grey_pieces_copy, depth - 1, False, alfa, beta)
                        evals.append(eval)
                        if maxEval < eval:
                            maxEval = eval
                            best_piece = piece
                            best_move = move

            else:
                for piece, moves in self.get_all_movable_pieces_and_their_regular_moves(red_pieces):
                    for move in moves:
                        red_pieces_copy = copy.deepcopy(red_pieces)
                        grey_pieces_copy = copy.deepcopy(grey_pieces)
                        piece_to_move = self.getCheckerObject_2(red_pieces_copy, piece[0])
                        self.simulate_move((piece[0], piece_to_move), move)
                        _, _, eval = self.min_max(red_pieces_copy, grey_pieces_copy, depth - 1, False, alfa, beta)
                        evals.append(eval)
                        if maxEval < eval:
                            maxEval = eval
                            best_piece = piece
                            best_move = move
                        alfa = max(alfa, eval)
                        if beta <= alfa:
                            break
            return best_piece[0], best_move, maxEval

        else:
            evals = []
            minEval = float('inf')
            jump_moves = self.get_all_movable_pieces_and_their_jump_moves(grey_pieces)
            if len(jump_moves) > 0:
                for piece, moves in jump_moves:
                    for move in moves:
                        red_pieces_copy = copy.deepcopy(red_pieces)
                        grey_pieces_copy = copy.deepcopy(grey_pieces)
                        piece_to_move = self.getCheckerObject_2(grey_pieces_copy, piece[0])
                        self.simulate_jump_move((piece[0], piece_to_move), move, red_pieces_copy)
                        _, _, eval = self.min_max(red_pieces_copy, grey_pieces_copy, depth - 1, True, alfa, beta)
                        evals.append(eval)
                        if minEval > eval:
                            minEval = eval
                            best_piece = piece
                            best_move = move
            else:
                for piece, moves in self.get_all_movable_pieces_and_their_regular_moves(grey_pieces):
                    for move in moves:
                        red_pieces_copy = copy.deepcopy(red_pieces)
                        grey_pieces_copy = copy.deepcopy(grey_pieces)
                        piece_to_move = self.getCheckerObject_2(grey_pieces_copy, piece[0])
                        self.simulate_move((piece[0], piece_to_move), move)
                        _, _, eval = self.min_max(red_pieces_copy, grey_pieces_copy, depth - 1, True, alfa, beta)
                        evals.append(eval)
                        if minEval > eval:
                            minEval = eval
                            best_piece = piece
                            best_move = move
                        beta = min(beta, eval)
                        if beta <= alfa:
                            break
            return best_piece[0], best_move, minEval

    def min_max_def(self, red_pieces, grey_pieces, depth, maximizingPlayer):
        if depth == 0 or len(red_pieces) == 0 or len(grey_pieces) == 0:
            return 0, 0, self.evaluate_positions(grey_pieces)

        best_piece = (0, 0)
        best_move = (100, 100)
        if maximizingPlayer:
            minEval = float('inf')
            jump_moves = self.get_all_movable_pieces_and_their_jump_moves(red_pieces)
            if len(jump_moves) > 0:
                for piece, moves in jump_moves:
                    for move in moves:
                        red_pieces_copy = copy.deepcopy(red_pieces)
                        grey_pieces_copy = copy.deepcopy(grey_pieces)
                        piece_to_move = self.getCheckerObject_2(red_pieces_copy, piece[0])
                        self.simulate_jump_move((piece[0], piece_to_move), move, red_pieces_copy + grey_pieces_copy)
                        _, _, eval = self.min_max_def(red_pieces_copy, grey_pieces_copy, depth - 1, False)
                        if minEval > eval:
                            minEval = eval
                            best_piece = piece
                            best_move = move


            else:
                for piece, moves in self.get_all_movable_pieces_and_their_regular_moves(red_pieces):
                    for move in moves:
                        red_pieces_copy = copy.deepcopy(red_pieces)
                        grey_pieces_copy = copy.deepcopy(grey_pieces)
                        piece_to_move = self.getCheckerObject_2(red_pieces_copy, piece[0])
                        self.simulate_move((piece[0], piece_to_move), move)
                        _, _, eval = self.min_max_def(red_pieces_copy, grey_pieces_copy, depth - 1, False)
                        if minEval > eval:
                            minEval = eval
                            best_piece = piece
                            best_move = move

            return best_piece[0], best_move, minEval
        else:
            maxEval = float('-inf')
            jump_moves = self.get_all_movable_pieces_and_their_jump_moves(grey_pieces)
            if len(jump_moves) > 0:
                for piece, moves in jump_moves:
                    for move in moves:
                        red_pieces_copy = copy.deepcopy(red_pieces)
                        grey_pieces_copy = copy.deepcopy(grey_pieces)
                        piece_to_move = self.getCheckerObject_2(grey_pieces_copy, piece[0])
                        self.simulate_jump_move((piece[0], piece_to_move), move, red_pieces_copy + grey_pieces_copy)
                        _, _, eval = self.min_max_def(red_pieces_copy, grey_pieces_copy, depth - 1, True)
                        if maxEval < eval:
                            maxEval = eval
                            best_piece = piece
                            best_move = move
            else:
                for piece, moves in self.get_all_movable_pieces_and_their_regular_moves(grey_pieces):
                    for move in moves:
                        red_pieces_copy = copy.deepcopy(red_pieces)
                        grey_pieces_copy = copy.deepcopy(grey_pieces)
                        piece_to_move = self.getCheckerObject_2(grey_pieces_copy, piece[0])
                        self.simulate_move((piece[0], piece_to_move), move)
                        _, _, eval = self.min_max_def(red_pieces_copy, grey_pieces_copy, depth - 1, True)
                        if maxEval < eval:
                            maxEval = eval
                            best_piece = piece
                            best_move = move

            return best_piece[0], best_move, maxEval
